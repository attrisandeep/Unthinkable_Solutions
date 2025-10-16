"""
KnowledgeExplorer Embeddings Service
Jina AI Hub cloud client wrapper with fallback to sentence-transformers

Note: This uses Jina AI's REST API via httpx, not the Jina Python SDK.
No 'jina' package installation required - only JINA_API_KEY in .env.
"""

import logging
from typing import List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend_config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """
    Embeddings service with Jina AI Hub cloud as primary and 
    sentence-transformers as fallback.
    
    To swap to local model only:
    1. Set use_jina=False in __init__
    2. Or remove JINA_API_KEY from .env
    """
    
    def __init__(self):
        self.jina_api_key = settings.jina_api_key
        self.use_jina = bool(self.jina_api_key)
        self.local_model = None
        self.dimension = 768  # Default embedding dimension
        
        if self.use_jina:
            logger.info("🌐 Using Jina AI Hub cloud for embeddings")
        else:
            logger.info("🏠 Jina API key not found, loading local sentence-transformers model")
            self._load_local_model()
    
    def _load_local_model(self):
        """Load sentence-transformers model as fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers model: all-mpnet-base-v2")
            self.local_model = SentenceTransformer('all-mpnet-base-v2')
            self.dimension = 768
            logger.info("✅ Local model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load local model: {e}")
            raise RuntimeError("Could not initialize embeddings service") from e
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _embed_with_jina(self, texts: List[str]) -> List[List[float]]:
        """
        Embed texts using Jina AI Hub cloud API.
        
        API Documentation: https://jina.ai/embeddings/
        """
        url = "https://api.jina.ai/v1/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}"
        }
        payload = {
            "input": texts,
            "model": "jina-embeddings-v2-base-en"  # or jina-embeddings-v2-small-en
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract embeddings from response
            embeddings = [item["embedding"] for item in data["data"]]
            return embeddings
    
    def _embed_with_local(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using local sentence-transformers model."""
        if self.local_model is None:
            self._load_local_model()
        
        embeddings = self.local_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts and return embeddings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        
        Raises:
            Exception: If both Jina and local fallback fail
        """
        if not texts:
            return []
        
        try:
            if self.use_jina:
                try:
                    logger.debug(f"Embedding {len(texts)} texts with Jina")
                    embeddings = await self._embed_with_jina(texts)
                    return embeddings
                except Exception as e:
                    logger.warning(f"⚠️  Jina embedding failed: {e}. Falling back to local model.")
                    # Fallback to local model
                    if self.local_model is None:
                        self._load_local_model()
                    return self._embed_with_local(texts)
            else:
                logger.debug(f"Embedding {len(texts)} texts with local model")
                return self._embed_with_local(texts)
                
        except Exception as e:
            logger.error(f"❌ Embedding failed: {e}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string.
        
        Args:
            query: Query string to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embeddings = await self.embed_texts([query])
        return embeddings[0] if embeddings else []
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        return self.dimension


# Global embeddings service instance
embeddings_service = EmbeddingsService()
