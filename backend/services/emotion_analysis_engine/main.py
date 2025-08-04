"""
🎭 Emotion Analysis Engine

FastAPI service for real-time emotion detection and analysis.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from common.config import settings
from common.utils.logger import get_service_logger
from api.routes import router

logger = get_service_logger("emotion_engine")

# Create FastAPI app
app = FastAPI(
    title="Emotion Analysis Engine",
    description="🎭 Real-time facial emotion detection and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🎭 Emotion Analysis Engine starting up...")
    logger.info(f"📍 Service running on port {settings.emotion_analysis_port}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🎭 Emotion Analysis Engine shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.emotion_analysis_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
