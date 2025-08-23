# 🔐 EmoHunter Trust Commit System

A privacy-preserving blockchain-anchored commitment system for emotional health sessions, integrated with KiteAI for verifiable trust without compromising user privacy.

## 🎯 Overview

The Trust Commit System creates cryptographically verifiable commitments of EmoHunter therapy sessions while ensuring **zero personal information** is ever stored on-chain. It provides accountability and transparency for AI-powered emotional health services.

## ✨ Key Features

### 🔒 **Privacy-First Design**
- **Zero PII on-chain**: Only cryptographic hashes and metadata stored
- **User-scoped encryption**: Each user gets unique derived keys
- **Canonical determinism**: Consistent hash generation for verification

### 🛡️ **Cryptographic Security**
- **Ed25519 signatures**: Agent identity verification
- **HMAC-SHA256**: Tamper-proof commitment hashing
- **HKDF key derivation**: Secure per-user key generation
- **Canonical JSON**: Deterministic data serialization

### ⛓️ **Blockchain Integration**
- **KiteAI native**: First-class agent identity on Kite blockchain
- **Dual mode**: Simulation for development, real chain for production
- **Automatic fallback**: Graceful degradation if chain unavailable
- **Retry mechanism**: Failed commits queued for later anchoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EmoHunter     │    │  Trust Commit    │    │   KiteAI        │
│   Session       │───▶│     System       │───▶│  Blockchain     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ • Emotion data  │    │ • Hash session   │    │ • Anchor hash   │
│ • Conversation  │    │ • Sign commit    │    │ • Verify agent  │
│ • User consent  │    │ • Store receipt  │    │ • Return TX ID  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔄 Commitment Flow

1. **Session Processing**: EmoHunter processes emotion analysis and conversation
2. **Data Canonicalization**: Session metadata converted to canonical JSON
3. **Hash Generation**: HMAC-SHA256 hash created with user-derived key
4. **Agent Signing**: Ed25519 signature proves agent authenticity
5. **Chain Anchoring**: Commitment hash anchored on KiteAI blockchain
6. **Receipt Storage**: Local receipt stored for verification

## 📊 What Gets Committed

### ✅ **Included (Privacy-Safe)**
```json
{
  "session_id": "sess_abc123",
  "consent_id": "consent_xyz789", 
  "user_uid": "user_def456",
  "model_hashes": {
    "cnn": "sha256_emotion_model_hash",
    "llm": "sha256_conversation_model_hash",
    "tts": "sha256_voice_model_hash"
  },
  "risk_bucket": "med",
  "cost_cents": 150,
  "timestamp": 1724390000
}
```

### ❌ **Never Included**
- Actual conversation content
- Emotion detection results
- Personal identifiable information
- Voice recordings or transcripts
- Specific emotional states

## 🚀 Quick Start

### 1. Generate Keys
```bash
uv run python tools/gen_keys.py
```

### 2. Configure Environment
```bash
# Copy generated keys to .env
cp .env.example .env
# Edit .env with your keys
```

### 3. Start Trust Commit API
```bash
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Test Commitment
```bash
curl -X POST http://localhost:8000/trust/commit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "consent_id": "test_consent_456",
    "user_uid": "test_user_789",
    "model_hashes": {"cnn": "hash1", "llm": "hash2"},
    "risk_bucket": "low",
    "timestamp": 1724390000
  }'
```

## 🔌 API Endpoints

### `POST /trust/commit`
Create a new session commitment
- **Input**: Session metadata (no PII)
- **Output**: Commitment hash, transaction ID, agent signature

### `GET /trust/verify`
Verify an existing commitment
- **Input**: Transaction ID and session ID
- **Output**: Verification status and commitment details

### `GET /trust/health`
Check system health and configuration
- **Output**: System status, chain connectivity, crypto health

## 🌐 KiteAI Integration

### Agent Registration
```python
from kite_sdk import KiteClient

client = KiteClient(api_key="your_kite_api_key")
agent_info = client.register_agent_service({
    "name": "EmoHunter Trust Commit",
    "description": "Privacy-safe emotional health session commitment",
    "capabilities": ["session_commitment", "privacy_preservation"]
})
```

### Environment Configuration
```bash
KITE_API_KEY=api_key_your_actual_key_here
KITE_AGENT_SERVICE_ID=agent_your_service_id_here
CHAIN_ENABLED=true
AGENT_DID=did:kite:emohunter:your_agent_id
```

## 🧪 Testing

### Core Cryptographic Functions
```bash
uv run python -c "
from app.core.canonical import validate_canonical_determinism, TEST_DATA
from app.core.crypto import Ed25519Signer
assert validate_canonical_determinism(TEST_DATA, iterations=10)
signer = Ed25519Signer()
assert signer.verify(b'test', signer.sign(b'test'))
print('✅ All crypto tests passed')
"
```

### Integration Tests
```bash
uv run python test_trust_commit_integration.py
```

## 📁 Project Structure

```
app/
├── adapters/
│   └── kite_chain.py      # KiteAI blockchain adapter
├── api/
│   └── trust.py           # Trust commit API endpoints
├── core/
│   ├── canonical.py       # Canonical JSON serialization
│   └── crypto.py          # Cryptographic operations
├── db/
│   ├── models.py          # Database models
│   └── session.py         # Database session management
└── main.py                # FastAPI application

tools/
└── gen_keys.py            # Key generation utility

tests/
├── conftest.py            # Test configuration
└── test_trust_system.py   # Test suite
```

## 🔐 Security Features

### **Cryptographic Guarantees**
- **Integrity**: HMAC prevents tampering
- **Authenticity**: Ed25519 proves agent identity  
- **Non-repudiation**: Blockchain anchoring prevents denial
- **Privacy**: Zero PII exposure

### **Key Management**
- **Master key**: 32-byte secure random generation
- **User derivation**: HKDF with unique user context
- **Agent keys**: Ed25519 keypair for signing
- **Environment isolation**: Separate keys per environment

## 🚨 Privacy Compliance

### **GDPR Compliance**
- ✅ No personal data on blockchain
- ✅ User consent tracking via consent_id
- ✅ Right to erasure (only local data affected)
- ✅ Data minimization (only necessary metadata)

### **HIPAA Considerations**
- ✅ No PHI in commitments
- ✅ Cryptographic access controls
- ✅ Audit trail via blockchain
- ✅ Secure key management

## 📊 Monitoring & Analytics

### **Health Metrics**
- Commitment success rate
- Chain anchoring latency
- Cryptographic operation performance
- Error rates and retry statistics

### **Privacy Metrics**
- Zero PII leakage verification
- Key rotation compliance
- Access pattern analysis
- Consent tracking coverage

## 🛠️ Development

### **Dependencies**
```bash
# Core dependencies
uv add fastapi uvicorn sqlmodel pynacl cryptography

# KiteAI integration
uv add kite-sdk

# Development tools
uv add --dev pytest pytest-asyncio requests
```

### **Environment Setup**
```bash
# Generate development keys
uv run python tools/gen_keys.py

# Start development server
uv run python -m uvicorn app.main:app --reload
```

## 🚀 Deployment

### **Simulation Mode** (Development)
```bash
CHAIN_ENABLED=false
DATABASE_URL=sqlite:///./trust_commit.db
```

### **Production Mode** (KiteAI)
```bash
CHAIN_ENABLED=true
KITE_API_KEY=api_key_your_production_key
KITE_AGENT_SERVICE_ID=agent_your_production_id
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 📚 Documentation

- **[KITE_DEPLOYMENT_GUIDE.md](./KITE_DEPLOYMENT_GUIDE.md)** - Complete KiteAI deployment walkthrough
- **[BACKEND_FEATURES.md](./BACKEND_FEATURES.md)** - EmoHunter backend integration
- **API Documentation** - Available at `/docs` when server running

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/trust-commit-enhancement`
3. **Make changes** with tests
4. **Run test suite**: `uv run pytest`
5. **Submit pull request**

## 📄 License

This Trust Commit System is part of the EmoHunter project and follows the same licensing terms.

---

**🎉 The Trust Commit System provides verifiable accountability for AI emotional health services while maintaining absolute privacy protection.**
