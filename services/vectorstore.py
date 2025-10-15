"""
KnowledgeExplorer Vector Store Service
Pinecone wrapper for vector storage and retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from tenacity import retry, stop_after_attempt, wait_exponential

from backend_config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Pinecone vector store wrapper for document storage and retrieval.
    
    Debug tips:
    - Check Pinecone dashboard to verify index exists
    - Ensure dimension matches your embedding model (768 for mpnet, 1024 for jina-v2)
    - Verify PINECONE_ENV matches your Pinecone project region
    """
    
    def __init__(self):
        self.api_key = settings.pinecone_api_key
        self.environment = settings.pinecone_env
        self.index_name = settings.pinecone_index
        self.pc = None
        self.index = None
        
        if not self.api_key:
            logger.warning("⚠️  Pinecone API key not found. Vector store disabled.")
            return
        
        try:
            self.pc = Pinecone(api_key=self.api_key)
            logger.info(f"✅ Pinecone client initialized for environment: {self.environment}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone client: {e}")
    
    def init_index(self, dimension: int = 768, metric: str = "cosine") -> bool:
        """
        Initialize or connect to Pinecone index.
        
        Args:
            dimension: Embedding dimension (default 768 for all-mpnet-base-v2)
            metric: Distance metric (cosine, euclidean, or dotproduct)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.pc:
            logger.error("Pinecone client not initialized")
            return False
        
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                logger.info(f"✅ Index '{self.index_name}' created successfully")
            else:
                logger.info(f"📌 Connecting to existing index: {self.index_name}")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            # Get index stats
            stats = self.index.describe_index_stats()
            logger.info(f"📊 Index stats: {stats}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize index: {e}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Upsert vectors with metadata to Pinecone.
        
        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dicts (must match vectors length)
            ids: Optional list of IDs (will auto-generate if not provided)
            
        Returns:
            Dict with upserted count
        """
        if not self.index:
            raise RuntimeError("Index not initialized. Call init_index() first.")
        
        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata must have same length")
        
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        # Prepare vectors for upsert
        vectors_to_upsert = [
            {
                "id": vid,
                "values": vector,
                "metadata": meta
            }
            for vid, vector, meta in zip(ids, vectors, metadata)
        ]
        
        # Upsert in batches of 100
        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            response = self.index.upsert(vectors=batch)
            total_upserted += response.upserted_count
            logger.debug(f"Upserted batch {i//batch_size + 1}: {response.upserted_count} vectors")
        
        logger.info(f"✅ Upserted {total_upserted} vectors to Pinecone")
        return {"upserted_count": total_upserted}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_vector(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone index for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matches with id, score, and metadata
        """
        if not self.index:
            raise RuntimeError("Index not initialized. Call init_index() first.")
        
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            filter=filter,
            include_metadata=include_metadata
        )
        
        # Format results
        results = []
        for match in response.matches:
            result = {
                "id": match.id,
                "score": match.score,
            }
            if include_metadata and hasattr(match, 'metadata'):
                result["metadata"] = match.metadata
            results.append(result)
        
        logger.info(f"🔍 Query returned {len(results)} results")
        return results
    
    def delete_by_filter(self, filter: Dict[str, Any]) -> Dict[str, str]:
        """
        Delete vectors matching a metadata filter.
        
        Args:
            filter: Metadata filter dict
            
        Returns:
            Status dict
        """
        if not self.index:
            raise RuntimeError("Index not initialized. Call init_index() first.")
        
        self.index.delete(filter=filter)
        logger.info(f"🗑️  Deleted vectors matching filter: {filter}")
        return {"status": "deleted"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if not self.index:
            raise RuntimeError("Index not initialized. Call init_index() first.")
        
        return self.index.describe_index_stats()


# Global vector store service instance
vectorstore_service = VectorStoreService()
