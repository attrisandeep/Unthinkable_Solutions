"""
KnowledgeExplorer Document Ingestion Pipeline
Loaders for PDF & TXT with chunking and vector storage
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from backend_config import settings
from services.embeddings import embeddings_service
from services.vectorstore import vectorstore_service

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Document ingestion pipeline that:
    1. Loads documents (PDF/TXT)
    2. Splits into chunks
    3. Generates embeddings
    4. Stores in Pinecone
    """
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(
            f"📝 Text splitter initialized: "
            f"chunk_size={settings.chunk_size}, "
            f"chunk_overlap={settings.chunk_overlap}"
        )
    
    def load_document(self, file_path: str) -> List[Any]:
        """
        Load a document based on file extension.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of LangChain Document objects
            
        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        logger.info(f"📄 Loading document: {path.name}")
        
        try:
            if extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif extension == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {extension}. Only PDF and TXT are supported.")
            
            documents = loader.load()
            logger.info(f"✅ Loaded {len(documents)} page(s) from {path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to load document {path.name}: {e}")
            raise
    
    def chunk_documents(self, documents: List[Any]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks with metadata.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of chunk dicts with text and metadata
        """
        logger.info(f"✂️  Splitting {len(documents)} document(s) into chunks...")
        
        chunks = []
        for doc_idx, doc in enumerate(documents):
            # Split document
            splits = self.text_splitter.split_text(doc.page_content)
            
            # Create chunk metadata
            for chunk_idx, chunk_text in enumerate(splits):
                chunk = {
                    "text": chunk_text,
                    "metadata": {
                        "chunk_id": f"{doc_idx}_{chunk_idx}",
                        "doc_index": doc_idx,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(splits),
                        **doc.metadata  # Include original metadata (page, source, etc.)
                    }
                }
                chunks.append(chunk)
        
        logger.info(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    async def ingest_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Complete ingestion pipeline for a single file.
        
        Args:
            file_path: Full path to the file
            filename: Original filename for metadata
            
        Returns:
            Dict with ingestion stats
        """
        logger.info(f"🚀 Starting ingestion pipeline for: {filename}")
        
        try:
            # Step 1: Load document
            documents = self.load_document(file_path)
            
            # Step 2: Chunk documents
            chunks = self.chunk_documents(documents)
            
            if not chunks:
                logger.warning(f"⚠️  No chunks generated for {filename}")
                return {
                    "filename": filename,
                    "status": "warning",
                    "message": "No content extracted",
                    "chunks": 0
                }
            
            # Step 3: Generate embeddings
            logger.info(f"🔢 Generating embeddings for {len(chunks)} chunks...")
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await embeddings_service.embed_texts(texts)
            
            # Step 4: Prepare metadata with filename
            metadata_list = []
            for chunk in chunks:
                meta = chunk["metadata"].copy()
                meta["filename"] = filename
                meta["text"] = chunk["text"][:500]  # Store preview in metadata
                metadata_list.append(meta)
            
            # Step 5: Generate unique IDs
            import uuid
            ids = [f"{filename}_{chunk['metadata']['chunk_id']}_{uuid.uuid4().hex[:8]}" 
                   for chunk in chunks]
            
            # Step 6: Upsert to Pinecone
            logger.info(f"💾 Upserting {len(embeddings)} vectors to Pinecone...")
            
            # Initialize index if not already done
            if not vectorstore_service.index:
                dimension = embeddings_service.get_dimension()
                vectorstore_service.init_index(dimension=dimension)
            
            result = vectorstore_service.upsert_vectors(
                vectors=embeddings,
                metadata=metadata_list,
                ids=ids
            )
            
            logger.info(f"✅ Ingestion complete for {filename}")
            return {
                "filename": filename,
                "status": "success",
                "chunks": len(chunks),
                "upserted": result.get("upserted_count", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed for {filename}: {e}")
            return {
                "filename": filename,
                "status": "error",
                "message": str(e),
                "chunks": 0
            }
    
    async def ingest_files(self, file_paths: List[tuple]) -> List[Dict[str, Any]]:
        """
        Ingest multiple files.
        
        Args:
            file_paths: List of (file_path, filename) tuples
            
        Returns:
            List of ingestion results
        """
        results = []
        for file_path, filename in file_paths:
            result = await self.ingest_file(file_path, filename)
            results.append(result)
        
        return results


# Global ingestion pipeline instance
ingestion_pipeline = IngestionPipeline()
