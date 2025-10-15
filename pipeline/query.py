"""
KnowledgeExplorer Query Pipeline
RAG query processing with retrieval and generation
"""

import logging
from typing import List, Dict, Any, Iterator

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
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Pinecone.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to retrieve (default: self.top_k)
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        if top_k is None:
            top_k = self.top_k
        
        logger.info(f"🔍 Querying Pinecone for top {top_k} results...")
        
        # Initialize index if needed
        if not vectorstore_service.index:
            dimension = len(query_vector)
            vectorstore_service.init_index(dimension=dimension)
        
        results = vectorstore_service.query_vector(
            query_vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results for RAG prompt
        documents = []
        for result in results:
            doc = {
                "id": result["id"],
                "score": result["score"],
                "text": result["metadata"].get("text", ""),
                "filename": result["metadata"].get("filename", "unknown"),
                "chunk_id": result["metadata"].get("chunk_id", ""),
                "metadata": result["metadata"]
            }
            documents.append(doc)
        
        logger.info(f"✅ Retrieved {len(documents)} documents")
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
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Complete query pipeline (non-streaming).
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Step 1: Embed question
            query_vector = await self.embed_question(question)
            
            # Step 2: Retrieve documents
            documents = self.retrieve_documents(query_vector, top_k)
            
            if not documents:
                logger.warning("⚠️  No documents retrieved")
                return {
                    "answer": "I don't have enough information to answer this question. Please upload relevant documents first.",
                    "sources": [],
                    "metadata": {
                        "retrieved_docs": 0,
                        "question": question
                    }
                }
            
            # Step 3: Build prompt
            prompt = self.build_prompt(question, documents)
            
            # Step 4: Generate answer
            answer = self.generate_answer(prompt)
            
            # Step 5: Format sources
            sources = [
                {
                    "filename": doc["filename"],
                    "chunk_id": doc["chunk_id"],
                    "score": doc["score"],
                    "preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
                }
                for doc in documents
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "metadata": {
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
        top_k: int = None
    ) -> Iterator[str]:
        """
        Complete query pipeline with streaming (SSE format).
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            
        Yields:
            SSE-formatted event strings
        """
        try:
            # Step 1: Embed question
            query_vector = await self.embed_question(question)
            
            # Step 2: Retrieve documents
            documents = self.retrieve_documents(query_vector, top_k)
            
            # Send sources metadata
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
                "sources": sources,
                "retrieved_docs": len(documents),
                "question": question
            }
            
            if not documents:
                # No documents found
                yield llm_service.format_sse_event("metadata", metadata)
                yield llm_service.format_sse_event("message", "I don't have enough information to answer this question. ")
                yield llm_service.format_sse_event("message", "Please upload relevant documents first.")
                yield llm_service.format_sse_event("done", {
                    "answer": "I don't have enough information to answer this question. Please upload relevant documents first.",
                    "sources": []
                })
                return
            
            # Step 3: Build prompt
            prompt = self.build_prompt(question, documents)
            
            # Step 4: Stream answer with metadata
            for event in llm_service.stream_sse_tokens(prompt, metadata=metadata):
                yield event
            
        except Exception as e:
            logger.error(f"❌ Stream query pipeline failed: {e}")
            yield llm_service.format_sse_event("error", {"error": str(e)})


# Global query pipeline instance
query_pipeline = QueryPipeline(top_k=5)
