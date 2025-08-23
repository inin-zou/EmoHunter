#!/usr/bin/env python3
"""
Test suite for Trust Commit System
Tests cryptographic operations, API endpoints, and chain integration
"""

import pytest
import os
import tempfile
import asyncio
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.crypto import (
    hmac_sha256, derive_user_key, Ed25519Signer
)
from app.core.canonical import canonical_json, validate_canonical_determinism, TEST_DATA
from app.db.session import get_async_session
from app.db.models import Receipt, ChainAnchor


# Test configuration
TEST_MASTER_KEY = "dGVzdF9tYXN0ZXJfa2V5XzEyMzQ1Njc4OTBhYmNkZWZnaGlqa2xtbm9wcXJzdA=="  # 32 bytes
TEST_AGENT_SK = "MC4CAQAwBQYDK2VwBCIEIGVzdF9hZ2VudF9zZWNyZXRfa2V5XzEyMzQ1Njc4OTA="


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    """Create test client with environment variables"""
    os.environ["MASTER_KEY"] = TEST_MASTER_KEY
    os.environ["AGENT_SK"] = TEST_AGENT_SK
    os.environ["AGENT_DID"] = "did:kite:emohunter:test"
    os.environ["CHAIN_ENABLED"] = "false"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    with TestClient(app) as client:
        yield client


class TestCanonicalJSON:
    """Test canonical JSON serialization"""
    
    def test_canonical_json_determinism(self):
        """Test that canonical_json produces deterministic output"""
        assert validate_canonical_determinism(TEST_DATA, iterations=10)
    
    def test_canonical_json_key_ordering(self):
        """Test that keys are sorted lexicographically"""
        data = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(data)
        expected = b'{"a":2,"m":3,"z":1}'
        assert result == expected
    
    def test_canonical_json_empty_field_removal(self):
        """Test that empty fields are removed"""
        data = {
            "valid": "value",
            "null_field": None,
            "empty_string": "",
            "empty_dict": {},
            "empty_list": []
        }
        result = canonical_json(data)
        expected = b'{"valid":"value"}'
        assert result == expected
    
    def test_canonical_json_nested_dict_ordering(self):
        """Test that nested dictionaries are properly ordered"""
        data = {
            "model_hashes": {
                "tts": "h_tts",
                "cnn": "h_cnn",
                "llm": "h_llm"
            }
        }
        result = canonical_json(data)
        # Should have alphabetically ordered keys in nested dict
        assert b'"cnn":"h_cnn"' in result
        assert result.find(b'"cnn"') < result.find(b'"llm"')
        assert result.find(b'"llm"') < result.find(b'"tts"')


class TestCryptography:
    """Test cryptographic operations"""
    
    def test_hmac_stability(self):
        """Test that HMAC produces consistent results"""
        key = b"test_key_32_bytes_long_padding_xx"
        data = b"test_data"
        
        hash1 = hmac_sha256(key, data)
        hash2 = hmac_sha256(key, data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # Hex string length
    
    def test_user_key_derivation(self):
        """Test user-scoped key derivation"""
        import base64
        master_key = base64.b64decode(TEST_MASTER_KEY)
        
        key1 = derive_user_key(master_key, "user123")
        key2 = derive_user_key(master_key, "user123")
        key3 = derive_user_key(master_key, "user456")
        
        assert key1 == key2  # Same user, same key
        assert key1 != key3  # Different user, different key
        assert len(key1) == 32  # 32 bytes
    
    def test_ed25519_sign_verify(self):
        """Test Ed25519 signing and verification"""
        signer = Ed25519Signer()
        data = b"test_message"
        
        signature = signer.sign(data)
        assert signer.verify(data, signature)
        
        # Test with different data
        assert not signer.verify(b"different_data", signature)
        
        # Test signature format
        import base64
        base64.b64decode(signature)  # Should not raise exception


class TestTrustAPI:
    """Test Trust Commit API endpoints"""
    
    def test_commit_endpoint_success(self, client):
        """Test successful commit creation"""
        commit_data = {
            "session_id": "test_session_123",
            "consent_id": "test_consent_456", 
            "user_uid": "test_user_789",
            "model_hashes": {
                "cnn": "hash_cnn_123",
                "llm": "hash_llm_456",
                "tts": "hash_tts_789"
            },
            "risk_bucket": "low",
            "cost_cents": 50,
            "timestamp": 1724390000
        }
        
        response = client.post("/trust/commit", json=commit_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "commit_hash" in data
        assert "tx_id" in data
        assert "agent_did" in data
        assert "signature" in data
        assert data["agent_did"] == "did:kite:emohunter:test"
    
    def test_commit_idempotency(self, client):
        """Test that duplicate commits return same result"""
        commit_data = {
            "session_id": "idempotent_test",
            "consent_id": "test_consent",
            "user_uid": "test_user",
            "model_hashes": {"cnn": "hash1"},
            "risk_bucket": "low",
            "timestamp": 1724390000
        }
        
        # First commit
        response1 = client.post("/trust/commit", json=commit_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second commit with same session_id
        response2 = client.post("/trust/commit", json=commit_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should return identical results
        assert data1["commit_hash"] == data2["commit_hash"]
        assert data1["signature"] == data2["signature"]
    
    def test_commit_validation_errors(self, client):
        """Test validation errors in commit endpoint"""
        # Missing required fields
        response = client.post("/trust/commit", json={})
        assert response.status_code == 422
        
        # Invalid risk_bucket
        invalid_data = {
            "session_id": "test",
            "consent_id": "test",
            "user_uid": "test",
            "model_hashes": {"cnn": "hash"},
            "risk_bucket": "invalid",  # Should be low|med|high
            "timestamp": 1724390000
        }
        response = client.post("/trust/commit", json=invalid_data)
        assert response.status_code == 422
        
        # Empty model_hashes
        empty_hashes_data = {
            "session_id": "test",
            "consent_id": "test", 
            "user_uid": "test",
            "model_hashes": {},  # Empty
            "risk_bucket": "low",
            "timestamp": 1724390000
        }
        response = client.post("/trust/commit", json=empty_hashes_data)
        assert response.status_code == 400
    
    def test_verify_endpoint_success(self, client):
        """Test successful verification"""
        # First create a commit
        commit_data = {
            "session_id": "verify_test_123",
            "consent_id": "test_consent",
            "user_uid": "test_user",
            "model_hashes": {"cnn": "hash1", "llm": "hash2"},
            "risk_bucket": "med",
            "cost_cents": 75,
            "timestamp": 1724390000
        }
        
        commit_response = client.post("/trust/commit", json=commit_data)
        assert commit_response.status_code == 200
        commit_data_resp = commit_response.json()
        
        # Then verify it
        verify_response = client.get(
            f"/trust/verify?tx_id={commit_data_resp['tx_id']}&session_id=verify_test_123"
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        assert verify_data["match"] is True
        assert verify_data["agent_did"] == "did:kite:emohunter:test"
        assert "details" in verify_data
    
    def test_verify_endpoint_not_found(self, client):
        """Test verification with non-existent session"""
        response = client.get("/trust/verify?tx_id=nonexistent&session_id=nonexistent")
        assert response.status_code == 404
    
    def test_health_endpoints(self, client):
        """Test health check endpoints"""
        # Main health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Trust health endpoint
        response = client.get("/trust/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestChainDisabledMode:
    """Test that system works with chain disabled"""
    
    def test_chain_disabled_still_works(self, client):
        """Test that commits work even when chain is disabled"""
        commit_data = {
            "session_id": "chain_disabled_test",
            "consent_id": "test_consent",
            "user_uid": "test_user", 
            "model_hashes": {"cnn": "hash1"},
            "risk_bucket": "high",
            "timestamp": 1724390000
        }
        
        response = client.post("/trust/commit", json=commit_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should still get a tx_id (simulated)
        assert "tx_id" in data
        assert data["tx_id"].startswith("tx_sim_") or data["tx_id"] == "pending"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
