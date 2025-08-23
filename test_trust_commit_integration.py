#!/usr/bin/env python3
"""
Integration test for Trust Commit System
Tests the complete flow: commit creation, verification, and API endpoints
"""

import os
import json
import requests
import time
from datetime import datetime

# Set environment variables for testing
os.environ["MASTER_KEY"] = "1KDKXae19v/8aGOv0ySHzw/1Ro4mKmhjRfJPfm+D6F8="
os.environ["AGENT_SK"] = "B7rnRm76Fb0CJI03UIh8dOJxWFenjIYQxAi7a4zedak="
os.environ["AGENT_DID"] = "did:kite:emohunter"
os.environ["CHAIN_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test_trust_commit.db"

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health check endpoints"""
    print("🏥 Testing health endpoints...")
    
    # Main health
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Main health endpoint working")
    
    # Trust health
    response = requests.get(f"{BASE_URL}/trust/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Trust health endpoint working")

def test_commit_creation():
    """Test creating a trust commit"""
    print("📝 Testing commit creation...")
    
    commit_data = {
        "session_id": f"test_session_{int(time.time())}",
        "consent_id": "test_consent_123",
        "user_uid": "test_user_456",
        "model_hashes": {
            "cnn": "sha256_cnn_hash_abc123",
            "llm": "sha256_llm_hash_def456",
            "tts": "sha256_tts_hash_ghi789"
        },
        "risk_bucket": "med",
        "cost_cents": 150,
        "timestamp": int(time.time())
    }
    
    response = requests.post(f"{BASE_URL}/trust/commit", json=commit_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "commit_hash" in data
    assert "tx_id" in data
    assert "agent_did" in data
    assert "signature" in data
    assert data["agent_did"] == "did:kite:emohunter"
    
    print(f"✓ Commit created successfully")
    print(f"  - Commit Hash: {data['commit_hash'][:16]}...")
    print(f"  - TX ID: {data['tx_id']}")
    print(f"  - Agent DID: {data['agent_did']}")
    
    return data, commit_data

def test_commit_verification(commit_response, original_data):
    """Test verifying a trust commit"""
    print("🔍 Testing commit verification...")
    
    tx_id = commit_response["tx_id"]
    session_id = original_data["session_id"]
    
    response = requests.get(f"{BASE_URL}/trust/verify", params={
        "tx_id": tx_id,
        "session_id": session_id
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["match"] is True
    assert data["agent_did"] == "did:kite:emohunter"
    assert "details" in data
    
    print("✓ Verification successful")
    print(f"  - Match: {data['match']}")
    print(f"  - Agent DID: {data['agent_did']}")
    
    return data

def test_idempotency():
    """Test that duplicate commits return same result"""
    print("🔄 Testing idempotency...")
    
    session_id = f"idempotent_test_{int(time.time())}"
    commit_data = {
        "session_id": session_id,
        "consent_id": "test_consent",
        "user_uid": "test_user",
        "model_hashes": {"cnn": "hash1", "llm": "hash2"},
        "risk_bucket": "low",
        "timestamp": int(time.time())
    }
    
    # First commit
    response1 = requests.post(f"{BASE_URL}/trust/commit", json=commit_data)
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Second commit with same session_id
    response2 = requests.post(f"{BASE_URL}/trust/commit", json=commit_data)
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Should return identical results
    assert data1["commit_hash"] == data2["commit_hash"]
    assert data1["signature"] == data2["signature"]
    assert data1["tx_id"] == data2["tx_id"]
    
    print("✓ Idempotency working correctly")

def test_validation_errors():
    """Test validation error handling"""
    print("⚠️ Testing validation errors...")
    
    # Missing required fields
    response = requests.post(f"{BASE_URL}/trust/commit", json={})
    assert response.status_code == 422
    print("✓ Missing fields validation working")
    
    # Invalid risk_bucket
    invalid_data = {
        "session_id": "test",
        "consent_id": "test",
        "user_uid": "test",
        "model_hashes": {"cnn": "hash"},
        "risk_bucket": "invalid",  # Should be low|med|high
        "timestamp": int(time.time())
    }
    response = requests.post(f"{BASE_URL}/trust/commit", json=invalid_data)
    assert response.status_code == 422
    print("✓ Invalid risk_bucket validation working")
    
    # Empty model_hashes
    empty_hashes_data = {
        "session_id": "test",
        "consent_id": "test",
        "user_uid": "test",
        "model_hashes": {},  # Empty
        "risk_bucket": "low",
        "timestamp": int(time.time())
    }
    response = requests.post(f"{BASE_URL}/trust/commit", json=empty_hashes_data)
    assert response.status_code == 400
    print("✓ Empty model_hashes validation working")

def main():
    """Run all integration tests"""
    print("🚀 Starting Trust Commit System Integration Tests")
    print("=" * 60)
    
    try:
        # Test health endpoints
        test_health_endpoints()
        print()
        
        # Test commit creation
        commit_response, original_data = test_commit_creation()
        print()
        
        # Test verification
        test_commit_verification(commit_response, original_data)
        print()
        
        # Test idempotency
        test_idempotency()
        print()
        
        # Test validation errors
        test_validation_errors()
        print()
        
        print("🎉 All integration tests passed!")
        print("=" * 60)
        print("✅ Trust Commit System is working correctly")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
