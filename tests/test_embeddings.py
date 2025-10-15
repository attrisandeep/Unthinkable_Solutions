"""
Test suite for KnowledgeExplorer embeddings service
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.embeddings import EmbeddingsService


@pytest.mark.asyncio
async def test_embed_texts_with_jina():
    """Test embedding with Jina API (mocked)."""
    with patch('services.embeddings.httpx.AsyncClient') as mock_client:
        # Mock Jina API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1] * 768},
                {"embedding": [0.2] * 768}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Create service with Jina enabled
        service = EmbeddingsService()
        service.use_jina = True
        service.jina_api_key = "test_key"
        
        # Test embedding
        texts = ["test text 1", "test text 2"]
        embeddings = await service.embed_texts(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 768
        assert embeddings[0][0] == 0.1


@pytest.mark.asyncio
async def test_embed_texts_with_local_fallback():
    """Test embedding with local model fallback (mocked)."""
    with patch('services.embeddings.SentenceTransformer') as mock_st:
        # Mock local model
        mock_model = Mock()
        mock_model.encode.return_value = [[0.3] * 768, [0.4] * 768]
        mock_st.return_value = mock_model
        
        # Create service without Jina
        service = EmbeddingsService()
        service.use_jina = False
        service._load_local_model()
        
        # Test embedding
        texts = ["test text 1", "test text 2"]
        embeddings = service._embed_with_local(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 768


@pytest.mark.asyncio
async def test_embed_query():
    """Test single query embedding."""
    with patch('services.embeddings.SentenceTransformer') as mock_st:
        # Mock local model
        mock_model = Mock()
        mock_model.encode.return_value = [[0.5] * 768]
        mock_st.return_value = mock_model
        
        service = EmbeddingsService()
        service.use_jina = False
        service._load_local_model()
        
        # Test query embedding
        embedding = await service.embed_query("test query")
        
        assert len(embedding) == 768
        assert embedding[0] == 0.5


def test_get_dimension():
    """Test getting embedding dimension."""
    with patch('services.embeddings.SentenceTransformer'):
        service = EmbeddingsService()
        service.use_jina = False
        
        dimension = service.get_dimension()
        assert dimension == 768


@pytest.mark.asyncio
async def test_embed_empty_list():
    """Test embedding empty list."""
    with patch('services.embeddings.SentenceTransformer'):
        service = EmbeddingsService()
        service.use_jina = False
        
        embeddings = await service.embed_texts([])
        assert embeddings == []
