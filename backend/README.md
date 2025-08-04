# EmoHunter Backend - Modular Microservices Architecture

🎭 **Real-time emotion detection and AI conversation system with blockchain incentives**

## Architecture Overview

The EmoHunter backend has been restructured into a modular microservices architecture. Currently, 2 services are active with 1 under development:

```
backend/
├── common/                            # Shared modules across all services
│   ├── config.py                      # Centralized configuration
│   ├── schemas/                       # Pydantic data models
│   │   ├── base.py                    # Base response models
│   │   ├── conversation.py            # Conversation-related schemas
│   │   ├── emotion.py                 # Emotion analysis schemas
│   │   └── incentive.py               # Incentive engine schemas
│   └── utils/
│       ├── logger.py                  # Logging utilities
│       └── helpers.py                 # Helper functions
│
├── services/
│   ├── emotion_analysis_engine/       # 🎭 Facial emotion detection
│   │   ├── main.py                    # FastAPI service entry
│   │   ├── api/routes.py              # Emotion detection endpoints
│   │   ├── services/emotion_detector.py # Core emotion detection logic
│   │   └── Dockerfile
│   │
│   ├── conversation_engine/           # 🤖 GPT + ElevenLabs integration
│   │   ├── main.py                    # FastAPI service entry
│   │   ├── api/routes.py              # Conversation endpoints
│   │   ├── services/
│   │   │   ├── gpt4o_client.py        # OpenAI GPT-4o integration
│   │   │   └── tts_client.py          # ElevenLabs TTS integration
│   │   └── Dockerfile
│   │
│   ├── incentive_engine/              # 🎯 Goal tracking & rewards (🚧 Under Development)
│   │   └── README.md                  # Development guide for team member
│   │
│   └── gateway/                       # 🌐 API Gateway
│       ├── main.py                    # Unified API entry point
│       ├── api/routes.py              # Gateway routing logic
│       └── Dockerfile
│
├── docker-compose.yml                 # Multi-service orchestration
└── README.md                          # This file
```

## Services Overview

### ✅ **Active Services**

#### 🎭 Emotion Analysis Engine (Port 8002)
- **Status**: ✅ **Active**
- **Purpose**: Real-time facial emotion detection using OpenCV and FER
- **Key Features**:
  - Camera stream processing
  - Emotion stability algorithms
  - Real-time emotion updates via Server-Sent Events
- **Endpoints**:
  - `GET /api/v1/current_emotion` - Get current detected emotion
  - `POST /api/v1/start_emotion_stream` - Start camera stream
  - `GET /api/v1/stream` - SSE stream for real-time updates

#### 🤖 Conversation Engine (Port 8001)
- **Status**: ✅ **Active**
- **Purpose**: Emotionally-aware conversation generation and text-to-speech
- **Key Features**:
  - GPT-4o integration for context-aware responses
  - ElevenLabs TTS with consistent voice synthesis
  - Conversation history management
- **Endpoints**:
  - `POST /api/v1/generate` - Generate text response
  - `POST /api/v1/talk` - Convert text to speech
  - `POST /api/v1/chat` - Combined conversation + TTS

#### 🌐 API Gateway (Port 8000)
- **Status**: ✅ **Active**
- **Purpose**: Unified entry point aggregating active microservices
- **Key Features**:
  - Service discovery and routing
  - Unified API for frontend consumption
  - Health monitoring of active services
- **Endpoints**:
  - Active service endpoints proxied through `/api/v1/`
  - `GET /api/v1/services/health` - Check active service health
  - `POST /api/v1/unified/emotion_chat` - Combined emotion + conversation workflow

### 🚧 **Under Development**

#### 🎯 Incentive Engine (Port 8003)
- **Status**: 🚧 **Under Development by Team Member**
- **Purpose**: Goal management and blockchain reward settlement
- **Planned Features**:
  - Emotion-based goal tracking
  - Progress monitoring and completion detection
  - Blockchain integration for reward settlement
- **Note**: Implementation in progress by another team member. See `services/incentive_engine/README.md` for development guide.

## Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Camera access (for emotion detection)
- API Keys:
  - OpenAI API key (for GPT-4o)
  - ElevenLabs API key (for TTS)

### Environment Setup

1. **Clone and navigate to the project**:
   ```bash
   cd backend/
   ```

2. **Set up environment variables**:
   ```bash
   cp ../.env.example .env
   # Edit .env with your API keys
   ```

3. **Required environment variables**:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   CAMERA_INDEX=0
   EMOTION_UPDATE_INTERVAL=1.0
   ```

### Running with Docker Compose (Recommended)

1. **Start active services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the active services**:
   - API Gateway: http://localhost:8000/docs (main entry point)
   - Emotion Analysis: http://localhost:8002/docs
   - Conversation Engine: http://localhost:8001/docs
   - ~~Incentive Engine: http://localhost:8003/docs~~ (under development)

3. **Stop all services**:
   ```bash
   docker-compose down
   ```

### Running Individual Services (Development)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run individual services**:
   ```bash
   # Emotion Analysis Engine
   cd services/emotion_analysis_engine && python main.py

   # Conversation Engine
   cd services/conversation_engine && python main.py

   # Incentive Engine
   cd services/incentive_engine && python main.py

   # API Gateway
   cd services/gateway && python main.py
   ```

## API Usage Examples

### Basic Emotion Detection
```bash
# Start emotion stream
curl -X POST "http://localhost:8000/api/v1/emotion/start_stream" \
  -H "Content-Type: application/json" \
  -d '{"camera_index": 0, "update_interval": 1.0}'

# Get current emotion
curl "http://localhost:8000/api/v1/emotion/current"
```

### Conversation with Emotion Context
```bash
# Generate emotionally-aware response
curl -X POST "http://localhost:8000/api/v1/conversation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am feeling stressed about work",
    "emotion_context": "sad"
  }'
```

### Goal Management (Under Development)
```bash
# Note: Incentive engine endpoints are currently under development
# These will be available once the incentive engine is implemented

# Create an emotion-based goal (TO BE IMPLEMENTED)
# curl -X POST "http://localhost:8000/api/v1/incentive/create_goal" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "description": "Stay happy for 5 minutes",
#     "target_emotion": "happy",
#     "duration_seconds": 300,
#     "reward_amount": 10.0
#   }'
```

### Unified Workflow
```bash
# Combined emotion detection + conversation (goal tracking under development)
curl -X POST "http://localhost:8000/api/v1/unified/emotion_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you doing today?",
    "user_id": "user123"
  }'
```

## Development

### Adding New Features

1. **Shared functionality**: Add to `common/` directory
2. **Service-specific features**: Add to respective service directory
3. **New endpoints**: Update both service routes and gateway routes
4. **Database models**: Add to `common/schemas/`

### Testing

```bash
# Run tests for all services
pytest

# Test individual service
cd services/emotion_analysis_engine && python -m pytest
```

### Monitoring and Logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f emotion-analysis
```

## Production Deployment

### With Database and Redis
```bash
# Start with optional database and caching
docker-compose --profile with-database --profile with-redis up -d
```

### Environment Variables for Production
```bash
# Security
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/emohunter
REDIS_URL=redis://localhost:6379

# CORS (restrict in production)
CORS_ORIGINS=["https://yourdomain.com"]
```

## Current System Status

### ✅ **Fully Operational**
- **🎭 Emotion Analysis Engine**: Real-time webcam emotion detection
- **🤖 Conversation Engine**: GPT-4o + ElevenLabs voice synthesis
- **🌐 API Gateway**: Unified access to active services

### 🚧 **In Development**
- **🎯 Incentive Engine**: Being implemented by another team member

## Architecture Benefits

1. **Scalability**: Each service can be scaled independently
2. **Maintainability**: Clear separation of concerns
3. **Fault Tolerance**: Service failures don't cascade to other components
4. **Technology Flexibility**: Each service can use different tech stacks
5. **Development Velocity**: Teams can work on services independently
6. **Parallel Development**: Incentive engine can be developed without affecting active services

## Future Enhancements

- [ ] **Complete Incentive Engine**: Goal tracking and blockchain reward settlement
- [ ] Add Redis caching for improved performance
- [ ] Implement PostgreSQL for data persistence
- [ ] Add blockchain integration for real reward settlement
- [ ] Implement service mesh for advanced networking
- [ ] Add monitoring and observability (Prometheus, Grafana)
- [ ] Implement authentication and authorization
- [ ] Add rate limiting and API quotas

## Troubleshooting

### Common Issues

1. **Camera not accessible**: Ensure camera permissions and `/dev/video0` access
2. **API keys not working**: Verify environment variables are set correctly
3. **Services not communicating**: Check Docker network configuration
4. **Port conflicts**: Ensure ports 8000-8003 are available

### Health Checks
```bash
# Check all services health
curl "http://localhost:8000/api/v1/services/health"
```

## Contributing

1. Follow the modular architecture patterns
2. Add appropriate error handling and logging
3. Update both service and gateway routes for new endpoints
4. Add tests for new functionality
5. Update documentation

---

Built with ❤️ for the Pond Hackathon 🎭🤖🎯
