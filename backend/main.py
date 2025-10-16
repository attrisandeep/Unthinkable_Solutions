"""
KnowledgeExplorer FastAPI Main Application
FastAPI app with CORS, health endpoints, and logging setup
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend_config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting KnowledgeExplorer backend...")
    logger.info(f"📋 Configuration: CHUNK_SIZE={settings.chunk_size}, CHUNK_OVERLAP={settings.chunk_overlap}")
    
    # Validate API keys
    validation = settings.validate_api_keys()
    logger.info(f"🔑 API Keys validation: {validation}")
    
    if not all(validation.values()):
        logger.warning("⚠️  Some API keys are missing. Check your .env file.")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down KnowledgeExplorer backend...")


# Initialize FastAPI app
app = FastAPI(
    title="KnowledgeExplorer API",
    description="RAG-powered document Q&A system with streaming support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Vite alternate port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level == "DEBUG" else "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "service": "KnowledgeExplorer API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with API key validation."""
    validation = settings.validate_api_keys()
    
    return {
        "status": "healthy",
        "api_keys": validation,
        "config": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "groq_model": settings.groq_model,
            "pinecone_index": settings.pinecone_index
        }
    }


@app.get("/api/health", tags=["Health"])
async def api_health():
    """API health endpoint."""
    return {"status": "ok"}


# Import and include routers
# Note: Import here to avoid circular dependencies
try:
    from routes.upload import router as upload_router
    from routes.query import router as query_router
    from routes.documents import router as documents_router
    
    app.include_router(upload_router, prefix="/api", tags=["Upload"])
    app.include_router(query_router, prefix="/api", tags=["Query"])
    app.include_router(documents_router, prefix="/api", tags=["Documents"])
    logger.info("✅ API routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️  Could not import routes: {e}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌐 Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
