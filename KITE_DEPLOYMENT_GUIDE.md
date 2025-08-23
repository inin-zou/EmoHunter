# 🚀 KiteAI Deployment Guide for EmoHunter Trust Commit

This guide walks you through deploying EmoHunter as an agent on the KiteAI blockchain to get real on-chain trust commit anchoring.

## 📋 Prerequisites

1. **KiteAI Account**: Sign up at [https://gokite.ai/](https://gokite.ai/)
2. **Agent Registration**: Register EmoHunter as an agent service
3. **API Key**: Obtain KiteAI API key with agent permissions

## 🔧 Step 1: Get KiteAI Credentials

### 1.1 Register on KiteAI Platform
```bash
# Visit https://gokite.ai/ and create account
# Navigate to agent registration section
```

### 1.2 Register EmoHunter Agent
```python
from kite_sdk import KiteClient

# Initialize client with your API key
client = KiteClient(api_key="your_kite_api_key_here")

# Register EmoHunter as agent service
service_registration = {
    "name": "EmoHunter Trust Commit",
    "description": "Privacy-safe emotional health session commitment system",
    "endpoints": [
        {
            "path": "/trust/commit",
            "method": "POST",
            "description": "Create privacy-safe session commitment"
        },
        {
            "path": "/trust/verify", 
            "method": "GET",
            "description": "Verify session commitment integrity"
        }
    ],
    "capabilities": [
        "session_commitment",
        "privacy_preservation", 
        "cryptographic_verification"
    ]
}

# This will return your unique agent service ID
agent_info = client.register_agent_service(service_registration)
print(f"Agent Service ID: {agent_info['service_id']}")
```

## 🔐 Step 2: Install KiteAI SDK

```bash
# Add KiteAI SDK to dependencies
uv add kite-sdk

# Or using pip
pip install kite-sdk
```

## ⚙️ Step 3: Configure Environment Variables

Update your `.env` file with KiteAI credentials:

```bash
# KiteAI Configuration
KITE_API_KEY=api_key_your_actual_api_key_here
KITE_AGENT_SERVICE_ID=agent_your_service_id_here

# Enable real chain mode
CHAIN_ENABLED=true

# Update Agent DID with your KiteAI agent ID
AGENT_DID=did:kite:emohunter:your_agent_id_here

# Existing Trust Commit configuration
MASTER_KEY=your_master_key_here
AGENT_SK=your_agent_secret_key_here
DATABASE_URL=sqlite:///./trust_commit.db
```

## 🔄 Step 4: Update KiteAI Chain Adapter

The `KiteChainAdapter` has been updated to support real KiteAI integration. Key features:

- **Automatic fallback**: Falls back to simulation if KiteAI SDK unavailable
- **Real chain anchoring**: Uses `client.call_service()` for on-chain commits
- **Error handling**: Queues failed commits for retry
- **Dual mode**: Supports both simulation and production

## 🧪 Step 5: Test KiteAI Integration

### 5.1 Test Agent Registration
```python
# Test script: test_kite_integration.py
import os
from kite_sdk import KiteClient

api_key = os.getenv("KITE_API_KEY")
service_id = os.getenv("KITE_AGENT_SERVICE_ID")

client = KiteClient(api_key=api_key)

# Get service information
service_info = client.get_service_info(service_id=service_id)
print("Service Info:", service_info)

# Test service call
test_commitment = {
    "action": "anchor_commitment",
    "data": {
        "agent_did": "did:kite:emohunter:test",
        "commit_hash": "test_hash_123",
        "timestamp": 1724390000,
        "cost_cents": 100
    }
}

response = client.call_service(service_id=service_id, inputs=test_commitment)
print("Commitment Response:", response)
```

### 5.2 Test Trust Commit with Real Chain
```bash
# Start EmoHunter with KiteAI integration
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test commitment creation
curl -X POST http://localhost:8000/trust/commit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "kite_test_session_123",
    "consent_id": "kite_consent_456", 
    "user_uid": "kite_user_789",
    "model_hashes": {
      "cnn": "kite_cnn_hash",
      "llm": "kite_llm_hash"
    },
    "risk_bucket": "med",
    "cost_cents": 150,
    "timestamp": 1724390000
  }'

# Response should include real KiteAI transaction ID
```

## 🔍 Step 6: Verify On-Chain Anchoring

### 6.1 Check Transaction Status
```python
# Verify commitment on KiteAI blockchain
tx_id = "your_transaction_id_from_response"

response = client.call_service(
    service_id=service_id,
    inputs={
        "action": "get_commitment", 
        "data": {"tx_id": tx_id}
    }
)

print("On-chain Commitment:", response)
```

### 6.2 Use Trust Verify Endpoint
```bash
# Verify through EmoHunter API
curl "http://localhost:8000/trust/verify?tx_id=your_tx_id&session_id=kite_test_session_123"
```

## 🌐 Step 7: MCP Server Integration (Optional)

Enable EmoHunter to work with MCP-compatible AI applications:

```bash
# MCP Server URL format
https://mcp.prod.gokite.ai/api_key_your_api_key_here/mcp
```

Configure in Claude Desktop or other MCP clients to enable:
- Agent identity verification
- Cross-platform authorization  
- Blockchain-native settlement

## 🏥 Step 8: Health Check

Verify KiteAI integration is working:

```bash
curl http://localhost:8000/trust/health
```

Expected response with KiteAI enabled:
```json
{
  "status": "healthy",
  "chain_enabled": true,
  "kite_integration": "active",
  "agent_service_id": "agent_your_service_id",
  "crypto_status": "operational"
}
```

## 🔐 Security Best Practices

1. **API Key Security**: Never commit API keys to version control
2. **Environment Isolation**: Use different keys for dev/staging/production
3. **Key Rotation**: Regularly rotate KiteAI API keys
4. **Access Control**: Limit agent permissions to minimum required
5. **Monitoring**: Monitor on-chain transaction costs and usage

## 🚨 Troubleshooting

### Common Issues:

**"kite_sdk not installed"**
```bash
uv add kite-sdk
```

**"Invalid API key"**
- Verify API key format: `api_key_...`
- Check KiteAI dashboard for key status

**"Service ID not found"**
- Ensure agent service is properly registered
- Verify service ID format: `agent_...`

**"Chain write failed"**
- Check KiteAI service status
- Verify agent has sufficient permissions
- Review error logs for specific issues

## 📊 Monitoring & Analytics

Monitor your KiteAI agent performance:

1. **Transaction Volume**: Track commitment anchoring frequency
2. **Cost Analysis**: Monitor blockchain transaction costs
3. **Error Rates**: Track failed vs successful commits
4. **Latency**: Measure on-chain anchoring response times

## 🎯 Next Steps

1. **Production Deployment**: Deploy to production with real KiteAI integration
2. **Scaling**: Configure auto-scaling for high-volume sessions
3. **Analytics**: Implement detailed trust commit analytics
4. **Integration**: Connect with other KiteAI agent services

---

**🎉 Congratulations!** EmoHunter is now deployed as a KiteAI agent with real blockchain trust commit anchoring.
