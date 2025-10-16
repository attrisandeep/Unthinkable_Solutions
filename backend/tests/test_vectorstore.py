"""
Test suite for KnowledgeExplorer vector store service
"""

import pytest
from unittest.mock import Mock, patch
from services.vectorstore import VectorStoreService


def test_vectorstore_init():
    """Test vector store initialization."""
    with patch('services.vectorstore.Pinecone') as mock_pinecone:
        mock_client = Mock()
        mock_pinecone.return_value = mock_client
        
        service = VectorStoreService()
        service.api_key = "test_key"
        service.pc = Pinecone(api_key="test_key")
        
        assert service.pc is not None


def test_init_index_creates_new():
    """Test creating a new index."""
    with patch('services.vectorstore.Pinecone') as mock_pinecone:
        mock_client = Mock()
        mock_client.list_indexes.return_value = []
        mock_client.create_index = Mock()
        mock_client.Index.return_value = Mock()
        mock_pinecone.return_value = mock_client
        
        service = VectorStoreService()
        service.api_key = "test_key"
        service.pc = mock_client
        
        result = service.init_index(dimension=768)
        
        assert result is True
        mock_client.create_index.assert_called_once()


def test_init_index_connects_existing():
    """Test connecting to existing index."""
    with patch('services.vectorstore.Pinecone') as mock_pinecone:
        mock_index_info = Mock()
        mock_index_info.name = "knowledge-explorer"
        
        mock_client = Mock()
        mock_client.list_indexes.return_value = [mock_index_info]
        mock_index = Mock()
        mock_index.describe_index_stats.return_value = {"total_vector_count": 100}
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        service = VectorStoreService()
        service.api_key = "test_key"
        service.pc = mock_client
        service.index_name = "knowledge-explorer"
        
        result = service.init_index(dimension=768)
        
        assert result is True
        assert service.index is not None


def test_upsert_vectors():
    """Test upserting vectors."""
    mock_index = Mock()
    mock_response = Mock()
    mock_response.upserted_count = 2
    mock_index.upsert.return_value = mock_response
    
    service = VectorStoreService()
    service.index = mock_index
    
    vectors = [[0.1] * 768, [0.2] * 768]
    metadata = [{"text": "doc1"}, {"text": "doc2"}]
    
    result = service.upsert_vectors(vectors, metadata)
    
    assert result["upserted_count"] == 2
    mock_index.upsert.assert_called_once()


def test_upsert_vectors_validation():
    """Test upsert validation."""
    service = VectorStoreService()
    service.index = Mock()
    
    vectors = [[0.1] * 768]
    metadata = [{"text": "doc1"}, {"text": "doc2"}]
    
    with pytest.raises(ValueError):
        service.upsert_vectors(vectors, metadata)


def test_query_vector():
    """Test querying vectors."""
    mock_match = Mock()
    mock_match.id = "doc1"
    mock_match.score = 0.95
    mock_match.metadata = {"text": "test"}
    
    mock_response = Mock()
    mock_response.matches = [mock_match]
    
    mock_index = Mock()
    mock_index.query.return_value = mock_response
    
    service = VectorStoreService()
    service.index = mock_index
    
    query_vector = [0.1] * 768
    results = service.query_vector(query_vector, top_k=5)
    
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["score"] == 0.95
    assert results[0]["metadata"]["text"] == "test"


def test_get_stats():
    """Test getting index stats."""
    mock_index = Mock()
    mock_index.describe_index_stats.return_value = {
        "total_vector_count": 100,
        "dimension": 768
    }
    
    service = VectorStoreService()
    service.index = mock_index
    
    stats = service.get_stats()
    
    assert stats["total_vector_count"] == 100
    assert stats["dimension"] == 768


def test_query_without_index():
    """Test querying without initialized index."""
    service = VectorStoreService()
    service.index = None
    
    with pytest.raises(RuntimeError):
        service.query_vector([0.1] * 768)
