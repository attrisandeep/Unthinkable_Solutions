"""
KnowledgeExplorer Document Management Routes
Endpoints for listing, filtering, and deleting documents
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.vectorstore import vectorstore_service

logger = logging.getLogger(__name__)

router = APIRouter()


class DeleteResponse(BaseModel):
    """Response model for delete endpoints."""
    status: str
    message: str


class StatsResponse(BaseModel):
    """Response model for stats endpoint."""
    total_vectors: int
    dimensions: int
    namespaces: dict


@router.get("/documents/stats", response_model=StatsResponse)
async def get_document_stats():
    """
    Get statistics about stored documents.
    
    Returns:
        StatsResponse with index statistics
    """
    try:
        stats = vectorstore_service.get_stats()
        
        total_vectors = stats.total_vector_count
        dimensions = stats.dimension
        namespaces = stats.namespaces
        
        logger.info(f"📊 Stats requested: {total_vectors} vectors")
        
        return StatsResponse(
            total_vectors=total_vectors,
            dimensions=dimensions,
            namespaces=namespaces
        )
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/filename/{filename}", response_model=DeleteResponse)
async def delete_document_by_filename(filename: str):
    """
    Delete all chunks from a specific document.
    
    Args:
        filename: Name of the document to delete
        
    Returns:
        DeleteResponse with deletion status
    """
    try:
        logger.info(f"🗑️  Deleting all chunks for: {filename}")
        result = vectorstore_service.delete_by_filename(filename)
        
        return DeleteResponse(
            status="success",
            message=f"Deleted all chunks from document: {filename}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to delete document {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/clear-all", response_model=DeleteResponse)
async def clear_all_documents():
    """
    Delete ALL documents from the vector store.
    ⚠️  WARNING: This action cannot be undone!
    
    Returns:
        DeleteResponse with deletion status
    """
    try:
        logger.warning("⚠️  CLEARING ALL DOCUMENTS - This action cannot be undone!")
        result = vectorstore_service.clear_all_documents()
        
        return DeleteResponse(
            status="success",
            message="All documents have been deleted from the knowledge base"
        )
    except Exception as e:
        logger.error(f"❌ Failed to clear all documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
