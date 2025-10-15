"""
KnowledgeExplorer Upload Routes
File upload endpoint with document ingestion
"""

import logging
import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend_config import settings
from pipeline.ingest import ingestion_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    status: str
    message: str
    files: List[dict]


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload and ingest PDF/TXT files.
    
    Accepts multiple files, saves them to ./uploads, and triggers
    the ingestion pipeline for each file.
    
    Args:
        files: List of uploaded files
        
    Returns:
        UploadResponse with ingestion results
        
    Raises:
        HTTPException: If file type is invalid or ingestion fails
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    logger.info(f"📤 Received {len(files)} file(s) for upload")
    
    # Validate file types
    allowed_extensions = {".pdf", ".txt"}
    results = []
    file_paths = []
    
    for file in files:
        # Check file extension
        extension = Path(file.filename).suffix.lower()
        
        if extension not in allowed_extensions:
            logger.warning(f"⚠️  Rejected file {file.filename}: unsupported type {extension}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Unsupported file type. Only PDF and TXT files are allowed.",
                "chunks": 0
            })
            continue
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.max_upload_size:
            logger.warning(f"⚠️  Rejected file {file.filename}: too large ({file_size} bytes)")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"File too large. Maximum size is {settings.max_upload_size} bytes.",
                "chunks": 0
            })
            continue
        
        # Save file
        try:
            file_path = os.path.join(settings.upload_dir, file.filename)
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"💾 Saved file: {file.filename} ({file_size} bytes)")
            file_paths.append((file_path, file.filename))
            
        except Exception as e:
            logger.error(f"❌ Failed to save file {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Failed to save file: {str(e)}",
                "chunks": 0
            })
    
    # Ingest files
    if file_paths:
        logger.info(f"🚀 Starting ingestion for {len(file_paths)} file(s)...")
        ingestion_results = await ingestion_pipeline.ingest_files(file_paths)
        results.extend(ingestion_results)
    
    # Determine overall status
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    if error_count == len(results):
        status = "error"
        message = "All files failed to process"
    elif success_count > 0:
        status = "success"
        message = f"Successfully processed {success_count} file(s)"
        if error_count > 0:
            message += f", {error_count} failed"
    else:
        status = "partial"
        message = "Some files processed successfully"
    
    logger.info(f"✅ Upload complete: {success_count} success, {error_count} errors")
    
    return UploadResponse(
        status=status,
        message=message,
        files=results
    )


@router.get("/upload/status")
async def upload_status():
    """
    Get upload directory status.
    
    Returns:
        Dict with upload directory info
    """
    upload_dir = Path(settings.upload_dir)
    
    if not upload_dir.exists():
        return {
            "exists": False,
            "file_count": 0,
            "files": []
        }
    
    files = list(upload_dir.iterdir())
    file_info = [
        {
            "name": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime
        }
        for f in files if f.is_file()
    ]
    
    return {
        "exists": True,
        "file_count": len(file_info),
        "files": file_info
    }
