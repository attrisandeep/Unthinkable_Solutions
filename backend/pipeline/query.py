"""
KnowledgeExplorer Query Pipeline
RAG query processing with retrieval and generation
"""

import logging
from typing import List, Dict, Any, Iterator, Optional

from backend_config import settings
from services.embeddings import embeddings_service
from services.vectorstore import vectorstore_service
from services.llm import llm_service

logger = logging.getLogger(__name__)


class QueryPipeline:
    """
    RAG query pipeline that:
    1. Embeds the question
    2. Retrieves relevant documents from Pinecone
    3. Builds RAG prompt with sources
    4. Generates answer using Groq LLM
    5. Returns answer with citations
    """
    
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        logger.info(f"🔍 Query pipeline initialized with top_k={top_k}")
    
    async def embed_question(self, question: str) -> List[float]:
        """
        Embed the user's question.
        
        Args:
            question: User's question string
            
        Returns:
            Embedding vector
        """
        logger.info(f"🔢 Embedding question: {question[:100]}...")
        embedding = await embeddings_service.embed_query(question)
        return embedding
    
    def retrieve_documents(
        self,
        query_vector: List[float],
        top_k: int = None,
        filename_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Pinecone with filtering.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to retrieve (default: self.top_k)
            filename_filter: Optional filename to filter results
            min_score: Minimum relevance score threshold (default: from settings)
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        if top_k is None:
            top_k = self.top_k
        
        if min_score is None:
            min_score = settings.min_relevance_score
        
        logger.info(f"🔍 Querying Pinecone for top {top_k} results (min_score: {min_score})...")
        
        # Initialize index if needed
        if not vectorstore_service.index:
            dimension = len(query_vector)
            vectorstore_service.init_index(dimension=dimension)
        
        # Build filter if filename specified
        filter_dict = None
        if filename_filter:
            filter_dict = {"filename": {"$eq": filename_filter}}
            logger.info(f"📄 Filtering by filename: {filename_filter}")
        
        results = vectorstore_service.query_vector(
            query_vector=query_vector,
            top_k=top_k * 2,  # Retrieve more to filter by score
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format and filter results
        documents = []
        for result in results:
            score = result["score"]
            
            # Apply relevance threshold
            if score < min_score:
                logger.debug(f"⚠️  Skipping low-relevance result (score: {score:.3f})")
                continue
            
            doc = {
                "id": result["id"],
                "score": score,
                "text": result["metadata"].get("text", ""),
                "filename": result["metadata"].get("filename", "unknown"),
                "chunk_id": result["metadata"].get("chunk_id", ""),
                "metadata": result["metadata"]
            }
            documents.append(doc)
            
            # Stop when we have enough high-quality results
            if len(documents) >= top_k:
                break
        
        logger.info(f"✅ Retrieved {len(documents)} high-relevance documents (>{min_score})")
        return documents
    
    def build_prompt(
        self,
        question: str,
        documents: List[Dict[str, Any]]
    ) -> str:
        """
        Build RAG prompt with question and retrieved documents.
        
        Args:
            question: User's question
            documents: Retrieved documents with metadata
            
        Returns:
            Formatted prompt string
        """
        prompt = llm_service.build_rag_prompt(
            question=question,
            contexts=documents
        )
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        """
        Generate answer using LLM.
        
        Args:
            prompt: RAG prompt with context
            
        Returns:
            Generated answer
        """
        logger.info("🤖 Generating answer with LLM...")
        answer = llm_service.generate(prompt)
        logger.info(f"✅ Generated answer ({len(answer)} chars)")
        return answer
    
    def stream_answer(self, prompt: str) -> Iterator[str]:
        """
        Stream answer tokens using LLM.
        
        Args:
            prompt: RAG prompt with context
            
        Yields:
            Token strings
        """
        logger.info("🤖 Streaming answer with LLM...")
        yield from llm_service.stream_tokens(prompt)
    
    async def query(
        self,
        question: str,
        top_k: int = None,
        force_documents: bool = False
    ) -> Dict[str, Any]:
        """
        Complete query pipeline with smart detection.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            force_documents: Force document usage even for general questions
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Check if question is document-related
            is_doc_question = llm_service.is_document_related_question(question)
            
            # Check if we have any documents
            stats = vectorstore_service.get_stats()
            has_documents = stats.total_vector_count > 0
            
            logger.info(f"📝 Question type: {'document-related' if is_doc_question else 'general'}")
            logger.info(f"📚 Documents available: {has_documents} ({stats.total_vector_count} vectors)")
            
            # Decide whether to use documents or general knowledge
            use_documents = (is_doc_question or force_documents) and has_documents
            
            if not use_documents:
                # Use general AI knowledge
                logger.info("🤖 Using general AI knowledge (no document retrieval)")
                prompt = llm_service.build_general_prompt(question)
                answer = self.generate_answer(prompt)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "metadata": {
                        "mode": "general",
                        "retrieved_docs": 0,
                        "question": question,
                        "message": "Answered using general AI knowledge"
                    }
                }
            
            # Use RAG pipeline with documents
            logger.info("📄 Using RAG pipeline with documents")
            
            # Step 1: Embed question
            query_vector = await self.embed_question(question)
            
            # Step 2: Retrieve documents
            documents = self.retrieve_documents(query_vector, top_k)
            
            if not documents:
                logger.warning("⚠️  No relevant documents found, falling back to general knowledge")
                prompt = llm_service.build_general_prompt(question)
                answer = self.generate_answer(prompt)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "metadata": {
                        "mode": "general_fallback",
                        "retrieved_docs": 0,
                        "question": question,
                        "message": "No relevant documents found. Answered using general knowledge."
                    }
                }
            
            # Step 3: Build prompt with context
            prompt = self.build_prompt(question, documents)
            
            # Step 4: Generate answer
            answer = self.generate_answer(prompt)
            
            # Step 5: Format sources (clean, without scores in the answer)
            sources = [
                {
                    "filename": doc["filename"],
                    "chunk_id": doc["chunk_id"],
                    "score": doc["score"],
                    "preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
                }
                for doc in documents
            ]
            
            # Add clean source list at the end of answer if not already mentioned
            if sources and "source:" not in answer.lower():
                source_names = list(set([s["filename"] for s in sources]))
                if len(source_names) == 1:
                    answer += f"\n\nSource: {source_names[0]}"
                else:
                    answer += f"\n\nSources: {', '.join(source_names)}"
            
            return {
                "answer": answer,
                "sources": sources,
                "metadata": {
                    "mode": "rag",
                    "retrieved_docs": len(documents),
                    "question": question,
                    "top_k": top_k or self.top_k
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Query pipeline failed: {e}")
            raise
    
    async def stream_query(
        self,
        question: str,
        top_k: int = None,
        force_documents: bool = False
    ) -> Iterator[str]:
        """
        Complete query pipeline with streaming and smart detection.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            force_documents: Force document usage
            
        Yields:
            SSE-formatted event strings
        """
        try:
            # Check if question is document-related
            is_doc_question = llm_service.is_document_related_question(question)
            
            # Check if we have any documents
            stats = vectorstore_service.get_stats()
            has_documents = stats.total_vector_count > 0
            
            logger.info(f"📝 Streaming - Question type: {'document-related' if is_doc_question else 'general'}")
            logger.info(f"📚 Documents available: {has_documents}")
            
            # Decide whether to use documents
            use_documents = (is_doc_question or force_documents) and has_documents
            
            if not use_documents:
                # Use general AI knowledge
                logger.info("🤖 Streaming with general AI knowledge")
                
                metadata = {
                    "mode": "general",
                    "sources": [],
                    "retrieved_docs": 0,
                    "question": question
                }
                
                prompt = llm_service.build_general_prompt(question)
                
                yield llm_service.format_sse_event("metadata", metadata)
                
                # Stream the answer
                for event in llm_service.stream_sse_tokens(prompt, metadata=metadata):
                    yield event
                
                return
            
            # Use RAG pipeline with documents
            logger.info("📄 Streaming with RAG pipeline")
            
            # Step 1: Embed question
            query_vector = await self.embed_question(question)
            
            # Step 2: Retrieve documents
            documents = self.retrieve_documents(query_vector, top_k)
            
            # Send sources metadata (clean, without exposing scores in answer)
            sources = [
                {
                    "filename": doc["filename"],
                    "chunk_id": doc["chunk_id"],
                    "score": doc["score"],
                    "preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
                }
                for doc in documents
            ]
            
            metadata = {
                "mode": "rag" if documents else "general_fallback",
                "sources": sources,
                "retrieved_docs": len(documents),
                "question": question
            }
            
            if not documents:
                # No relevant documents found, use general knowledge
                logger.warning("⚠️  No relevant documents, streaming with general knowledge")
                prompt = llm_service.build_general_prompt(question)
                
                yield llm_service.format_sse_event("metadata", metadata)
                
                for event in llm_service.stream_sse_tokens(prompt, metadata=metadata):
                    yield event
                
                return
            
            # Step 3: Build prompt with documents
            prompt = self.build_prompt(question, documents)
            
            # Step 4: Stream answer with metadata
            for event in llm_service.stream_sse_tokens(prompt, metadata=metadata):
                yield event
            
        except Exception as e:
            logger.error(f"❌ Stream query pipeline failed: {e}")
            yield llm_service.format_sse_event("error", {"error": str(e)})


# Global query pipeline instance
query_pipeline = QueryPipeline(top_k=5)
