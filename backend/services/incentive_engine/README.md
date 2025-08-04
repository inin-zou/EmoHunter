# 🎯 Incentive Engine

**Status**: 🚧 Under Development by Team Member

## Overview
This service will handle goal management and blockchain reward settlement functionality.

## Planned Features
- Emotion-based goal tracking
- Progress monitoring and completion detection
- Blockchain integration for reward settlement
- User balance and transaction management

## Architecture
```
incentive_engine/
├── main.py                    # FastAPI service entry point
├── api/
│   └── routes.py             # Goal and reward endpoints
├── services/
│   ├── goal_detector.py      # Goal progress tracking logic
│   └── vault_client.py       # Blockchain reward settlement
└── Dockerfile                # Container configuration
```

## Expected Endpoints
- `POST /api/v1/create_goal` - Create emotion-based goals
- `POST /api/v1/check_goal` - Update goal progress
- `GET /api/v1/goals/active` - Get active goals
- `GET /api/v1/vault/balance/{user_id}` - Get user balance
- `GET /api/v1/vault/transactions/{user_id}` - Get transaction history

## Integration Points
- **Emotion Analysis Engine**: Receives current emotion data for goal progress
- **API Gateway**: Exposes unified endpoints at `/api/v1/incentive/*`
- **Common Schemas**: Uses `common/schemas/incentive.py` for data models

## Development Notes
- Service should run on port 8003
- Use shared configuration from `common/config.py`
- Follow the same FastAPI patterns as other services
- Include proper error handling and logging

## Getting Started
1. Implement `main.py` with FastAPI app setup
2. Create API routes in `api/routes.py`
3. Implement business logic in `services/`
4. Add Dockerfile for containerization
5. Update gateway routes to proxy incentive endpoints

---
*This service is part of the EmoHunter modular microservices architecture*
