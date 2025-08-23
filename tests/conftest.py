"""
Pytest configuration and shared fixtures for Trust Commit System tests
"""

import pytest
import os
import tempfile
import asyncio
from typing import AsyncGenerator, Generator
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_async_session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_env():
    """Set up test environment variables"""
    original_env = {}
    test_vars = {
        "MASTER_KEY": "dGVzdF9tYXN0ZXJfa2V5XzEyMzQ1Njc4OTBhYmNkZWZnaGlqa2xtbm9wcXJzdA==",
        "AGENT_SK": "MC4CAQAwBQYDK2VwBCIEIGVzdF9hZ2VudF9zZWNyZXRfa2V5XzEyMzQ1Njc4OTA=",
        "AGENT_DID": "did:kite:emohunter:test",
        "CHAIN_ENABLED": "false",
        "DATABASE_URL": "sqlite:///test_trust.db"
    }
    
    # Store original values
    for key in test_vars:
        original_env[key] = os.environ.get(key)
    
    # Set test values
    for key, value in test_vars.items():
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def test_db_engine():
    """Create test database engine"""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session"""
    with Session(test_db_engine) as session:
        yield session


@pytest.fixture
def test_client(test_env):
    """Create test client with proper environment"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_commit_data():
    """Sample commit data for testing"""
    return {
        "session_id": "test_session_12345",
        "consent_id": "test_consent_67890", 
        "user_uid": "test_user_abcdef",
        "model_hashes": {
            "cnn": "sha256_cnn_model_hash_123",
            "llm": "sha256_llm_model_hash_456",
            "tts": "sha256_tts_model_hash_789"
        },
        "risk_bucket": "med",
        "cost_cents": 125,
        "timestamp": 1724390000
    }
