#!/usr/bin/env python3
"""
EmoHunter Trust Commit System - Main FastAPI Application
Kite Mode: Privacy-safe session commitment with on-chain anchoring
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.trust import router as trust_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield


# Create FastAPI application
app = FastAPI(
    title="EmoHunter Trust Commit System",
    description="Privacy-safe session commitment with Kite blockchain anchoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trust_router, prefix="/trust", tags=["trust"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "EmoHunter Trust Commit System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_did": os.getenv("AGENT_DID", "did:kite:emohunter"),
        "chain_enabled": os.getenv("CHAIN_ENABLED", "false").lower() == "true"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
