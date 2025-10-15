"""
KnowledgeExplorer Query Routes
Query endpoints with standard and streaming responses
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from pipeline.query import query_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(..., min_length=1, description="The question to ask")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")


class SourceItem(BaseModel):
    """Source item in query response."""
    filename: str
    chunk_id: str
    score: float
    preview: str


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    sources: List[SourceItem]
    metadata: dict


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the knowledge base (non-streaming).
    
    Accepts a question, retrieves relevant documents, and generates
    an answer using the RAG pipeline.
    
    Args:
        request: QueryRequest with question and optional top_k
        
    Returns:
        QueryResponse with answer, sources, and metadata
        
    Raises:
        HTTPException: If query processing fails
    """
    logger.info(f"🔍 Processing query: {request.question[:100]}...")
    
    try:
        result = await query_pipeline.query(
            question=request.question,
            top_k=request.top_k
        )
        
        # Convert to response model
        sources = [
            SourceItem(**source)
            for source in result["sources"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/stream-query")
async def stream_query(
    question: str = Query(..., min_length=1, description="The question to ask"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of documents to retrieve")
):
    """
    Query the knowledge base with streaming response (SSE).
    
    Returns Server-Sent Events stream with:
    - metadata event: sources and retrieved documents info
    - message events: individual tokens as they are generated
    - done event: final answer and token count
    - error event: if an error occurs
    
    Args:
        question: The question to ask
        top_k: Number of documents to retrieve (default: 5)
        
    Returns:
        StreamingResponse with text/event-stream content
        
    Example SSE events:
        event: metadata
        data: {"sources": [...], "retrieved_docs": 5}
        
        event: message
        data: "The"
        
        event: message
        data: " answer"
        
        event: done
        data: {"answer": "The answer is...", "token_count": 50}
    
    Frontend usage:
        const eventSource = new EventSource('/api/stream-query?question=...');
        eventSource.addEventListener('message', (e) => {
            console.log('Token:', e.data);
        });
        eventSource.addEventListener('done', (e) => {
            const result = JSON.parse(e.data);
            console.log('Complete answer:', result.answer);
            eventSource.close();
        });
    """
    logger.info(f"🔍 Processing streaming query: {question[:100]}...")
    
    async def event_generator():
        """Generate SSE events from query pipeline."""
        try:
            async for event in query_pipeline.stream_query(question, top_k):
                yield event
        except Exception as e:
            logger.error(f"❌ Streaming query failed: {e}")
            # Send error event
            yield f"event: error\ndata: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


@router.get("/query/test")
async def test_query():
    """
    Test endpoint to verify query route is working.
    
    Returns:
        Simple status message
    """
    return {
        "status": "ok",
        "message": "Query route is working",
        "endpoints": {
            "POST /api/query": "Standard query endpoint",
            "GET /api/stream-query": "Streaming query endpoint (SSE)"
        }
    }
