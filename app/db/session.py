#!/usr/bin/env python3
"""
Database session management for Trust Commit System
SQLite database initialization and connection handling
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trust_commit.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Create engines
engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_session():
    """Get synchronous database session"""
    with SessionLocal() as session:
        yield session


async def get_async_session():
    """Get asynchronous database session"""
    async with AsyncSessionLocal() as session:
        yield session
