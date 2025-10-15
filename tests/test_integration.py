"""
Integration smoke tests for KnowledgeExplorer
Only runs if API keys are present in environment
"""

import pytest
import os
from backend_config import settings


# Skip all tests in this file if API keys are not configured
pytestmark = pytest.mark.skipif(
    not all([settings.groq_api_key, settings.pinecone_api_key, settings.jina_api_key]),
    reason="API keys not configured - set GROQ_API_KEY, PINECONE_API_KEY, JINA_API_KEY in .env"
)


@pytest.mark.asyncio
async def test_embeddings_service_integration():
    """Test embeddings service with real API."""
    from services.embeddings import embeddings_service
    
    texts = ["This is a test document", "Another test document"]
    embeddings = await embeddings_service.embed_texts(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
    assert all(isinstance(x, float) for x in embeddings[0])


@pytest.mark.asyncio
async def test_vectorstore_init_integration():
    """Test Pinecone initialization with real API."""
    from services.vectorstore import vectorstore_service
    from services.embeddings import embeddings_service
    
    dimension = embeddings_service.get_dimension()
    result = vectorstore_service.init_index(dimension=dimension)
    
    assert result is True
    assert vectorstore_service.index is not None


@pytest.mark.asyncio
async def test_llm_service_integration():
    """Test LLM service with real Groq API."""
    from services.llm import llm_service
    
    if not llm_service.available:
        pytest.skip("LLM service not available")
    
    prompt = "Say 'test passed' and nothing else."
    response = llm_service.generate(prompt)
    
    assert len(response) > 0
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_full_pipeline_integration():
    """Test complete ingestion and query pipeline."""
    from services.embeddings import embeddings_service
    from services.vectorstore import vectorstore_service
    from pipeline.query import query_pipeline
    
    # Initialize index
    dimension = embeddings_service.get_dimension()
    vectorstore_service.init_index(dimension=dimension)
    
    # Create test embeddings
    test_texts = ["The capital of France is Paris.", "Python is a programming language."]
    embeddings = await embeddings_service.embed_texts(test_texts)
    
    # Upsert to Pinecone
    metadata = [
        {"filename": "test.txt", "text": test_texts[0], "chunk_id": "0_0"},
        {"filename": "test.txt", "text": test_texts[1], "chunk_id": "0_1"}
    ]
    vectorstore_service.upsert_vectors(embeddings, metadata, ids=["test1", "test2"])
    
    # Query
    result = await query_pipeline.query("What is the capital of France?", top_k=2)
    
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0


@pytest.mark.asyncio
async def test_streaming_query_integration():
    """Test streaming query pipeline."""
    from pipeline.query import query_pipeline
    
    tokens = []
    async for event in query_pipeline.stream_query("What is Python?", top_k=2):
        tokens.append(event)
    
    assert len(tokens) > 0
    # Check for different event types
    event_types = [t.split('\n')[0] for t in tokens if t.startswith('event:')]
    assert 'event: metadata' in event_types[0] if event_types else True
