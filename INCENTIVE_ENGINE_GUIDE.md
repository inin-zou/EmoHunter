# EmoHunter Incentive Engine Guide

This guide covers the setup, deployment, and usage of the EmoHunter Incentive Engine.


## Note: Backend Service Removed

The local incentive engine backend service has been removed since:
- Frontend is deployed on Vercel
- Smart contracts are deployed on testnet
- Direct frontend-to-contract interaction is preferred

For reference implementations, see `contracts/reference/` directory.

## Overview

The Incentive Engine is a blockchain-based reward system that tracks user emotional engagement and distributes token rewards based on:
- Emotion diversity and intensity
- Session duration and consistency  
- Multi-tier reward system (Bronze, Silver, Gold, Platinum)

## Architecture

- **Smart Contract**: `contracts/src/EmoHunterIncentiveEngine.sol`
- **Backend Service**: `backend/services/incentive_engine/service.py`
- **Mock Service**: `backend/services/incentive_engine/mock_service.py`
- **Tests**: `backend/services/incentive_engine/test_local.py`

## Quick Start

1. **Configure Environment**:
   ```bash
   # All configuration is in root .env file
   # Key variables:
   # - WEB3_PROVIDER_URL
   # - INCENTIVE_CONTRACT_ADDRESS  
   # - BACKEND_PRIVATE_KEY
   ```

2. **Deploy Smart Contract**:
   ```bash
   cd contracts
   ./deploy_and_configure.sh
   ```

3. **Test Locally**:
   ```bash
   cd backend/services/incentive_engine
   python mock_service.py  # Mock service
   python test_local.py    # Run tests
   ```

4. **Deploy to Production**:
   ```bash
   ./deploy_incentive_engine.sh
   ```

## API Endpoints

- `POST /sessions/start` - Start emotion tracking session
- `POST /sessions/{session_id}/emotions` - Record emotion
- `POST /sessions/{session_id}/end` - End session and calculate rewards
- `GET /users/{address}/stats` - Get user statistics
- `GET /health` - Health check

## Reward Tiers

- **Bronze**: 10 ETH base reward (basic engagement)
- **Silver**: 25 ETH base reward (moderate engagement)  
- **Gold**: 50 ETH base reward (high engagement)
- **Platinum**: 100 ETH base reward (exceptional engagement)

## Integration

The incentive engine runs as a standalone FastAPI service on port 8003. 
Your main application can integrate by making HTTP requests to the incentive engine API.

Example integration:
```python
import httpx

async def start_emotion_session(user_address: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/sessions/start",
            json={"user_address": user_address}
        )
        return response.json()
```

## Deployment

The incentive engine can be deployed to Google Cloud Run using the provided deployment script.
All configuration is managed through environment variables in the root .env file.

## Security

- Multi-signature governance for contract updates
- Backend authorization for secure blockchain interactions
- Private key management through environment variables
- Rate limiting and input validation on all endpoints

## Monitoring

- Health check endpoint for service monitoring
- Comprehensive logging and error handling
- Metrics collection for performance monitoring

For detailed technical documentation, see the smart contract and service code.
