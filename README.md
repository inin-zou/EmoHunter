# EmoHunter 🎭

**Real-Time Emotion Detection & AI Voice Agent with Apple Watch Biometric Integration**

A production-ready FastAPI application that combines real-time facial emotion detection, Apple Watch biometric data analysis, and intelligent voice conversations. Built for the Pond Hackathon, EmoHunter creates emotionally-aware AI interactions using computer vision, physiological data analysis, natural language processing, and voice synthesis for comprehensive mental health monitoring.

## 🚀 Live Deployments

**✅ Multi-Platform Architecture**

- **🎭 EmoHunter Backend**: [https://emohunter-biometric-api-6106408799.us-central1.run.app](https://emohunter-biometric-api-6106408799.us-central1.run.app) *(Live with Apple Watch Integration)*
- **🌐 Vault Frontend**: [https://pond-hack-multi-sig-vault.vercel.app/](https://pond-hack-multi-sig-vault.vercel.app/)
- **📜 Smart Contracts**: [BSC Testnet - 0x3e27d1471e73BaB92D30A005218ba156Db13e76f](https://testnet.bscscan.com/address/0x3e27d1471e73BaB92D30A005218ba156Db13e76f#code)

### Architecture Overview
- **EmoHunter Backend**: Google Cloud Run deployment with emotion detection & simplified voice AI
- **Vault Frontend**: Deployed on Vercel with multi-sig vault functionality
- **Smart Contracts**: Deployed on BSC Testnet with incentive engine
- **Integration**: Multi-service architecture with cross-platform communication
- **Voice System**: Unified ElevenLabs TTS with consistent Rachel voice across all emotions

## ✨ Key Features

### 🎥 Real-Time Emotion Detection
- **Computer Vision**: OpenCV-powered webcam integration
- **Emotion Analysis**: Advanced facial emotion recognition with FER library
- **Real-Time Streaming**: WebSocket and Server-Sent Events support
- **Stability Engine**: Smart emotion persistence to prevent rapid changes
- **Browser Integration**: Direct camera frame processing from web clients

### 🤖 AI-Powered Voice Agent
- **Emotional Intelligence**: GPT-4o integration for context-aware conversations
- **Voice Synthesis**: ElevenLabs API with unified Rachel voice (consistent across all emotions)
- **Session Management**: Persistent conversation context and user tracking
- **Multi-Modal**: Text and audio response generation
- **Simplified Configuration**: Single voice settings for better maintainability

### 🏗️ Production Architecture
- **Modular Design**: Clean separation of services and concerns
- **Scalable Backend**: FastAPI with async/await patterns
- **Cloud Native**: Docker containerization with Google Cloud Run deployment
- **API-First**: RESTful endpoints with comprehensive documentation
- **Real-Time Communication**: WebSocket support for live interactions

## 🔄 Recent Improvements

### Voice Configuration Simplification
- **Unified Voice System**: Replaced emotion-based voice variations with single consistent Rachel voice
- **Simplified Settings**: Single configuration (stability: 0.70, similarity_boost: 0.80, style: 0.50)
- **Better Maintainability**: Reduced complexity while maintaining high-quality TTS
- **Consistent User Experience**: Same voice quality across all emotional contexts

### Deployment & Integration
- **Branch Integration**: Successfully merged `contracts` and `backend-dev-zou` branches into `main`
- **Dependency Resolution**: Fixed FastAPI/TensorFlow compatibility issues for GCP deployment
- **Docker Optimization**: Enhanced Dockerfile with comprehensive system dependencies
- **Clean Codebase**: Removed legacy files and consolidated documentation
- **Multi-Platform Ready**: Aligned architecture across GCP, Vercel, and BSC testnet

### Current Status
- **Voice System**: ✅ Simplified and deployed
- **Smart Contracts**: ✅ Live on BSC testnet
- **Vault Frontend**: ✅ Live on Vercel
- **Backend Deployment**: 🔄 In progress on GCP Cloud Run

## API Endpoints

### Emotion Detection
- `GET /current_emotion` - Get the current detected emotion (simple polling)
- `GET /start_emotion_stream` - Stream emotion detection results (Server-Sent Events)
- `GET /ws/emotions` - WebSocket endpoint for real-time updates
- `POST /analyze_frame` - Process camera frames from browser

### Voice Agent
- `POST /talk` - Generate speech based on text and emotion
  ```json
  {
    "text": "You seem tense. Would you like to take a break?",
    "emotion": "angry"  // optional, uses current detected emotion if not provided
  }
  ```

### Utility
- `GET /` - API welcome message
- `GET /emotions/available` - List available emotions and voice mappings
- `GET /health` - System status and camera info

### 🍎 Apple Watch Biometric Integration (NEW)
- `POST /api/v1/biometric/upload` - Upload Apple Watch biometric data
- `POST /api/v1/biometric/mock/{user_id}` - Generate mock biometric data for testing
- `GET /api/v1/biometric/context/{user_id}` - Get biometric emotional context
- `GET /api/v1/biometric/triggers/{user_id}` - Get biometric triggers and alerts
- `POST /api/v1/biometric/proactive_intervention/{user_id}` - Trigger proactive interventions
- `GET /integrated_analysis/{user_id}` - Combined facial emotion + biometric analysis

#### Key Features:
- **Multi-Condition Trigger Detection**: `IF (Resting HR > baseline + 15%) AND (HRV < baseline - 20%) AND (Sleep quality poor ≥ 3 days) THEN → "anxious state"`
- **Personalized Baselines**: Individual physiological normal values with deviation detection
- **CBT/DBT Integration**: Evidence-based therapeutic recommendations and interventions
- **Proactive Monitoring**: Background analysis with automatic intervention triggers
- **Wellness Scoring**: Comprehensive health assessment (0-100 scale)
- **Mock Data Generation**: Realistic fallback data for testing and demonstrations

## Setup

### 1. Setup Environment
```bash
# Create and activate virtual environment with uv
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env

# Edit .env with your API keys:
# ELEVENLABS_API_KEY=your_elevenlabs_key_here
# OPENAI_API_KEY=your_openai_key_here
```

### 3. Run Modular Backend
```bash
# Or run directly from backend directory
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Legacy backend (if needed)
python main.py
```

### 4. Test the Modular Architecture
```bash
# Run comprehensive modular architecture test suite
python test_modular_architecture.py

# Or test legacy components
python test_client.py
python test_new_architecture.py
```

## Emotion to Voice Mapping

| Emotion | ElevenLabs Voice | Characteristics |
|---------|------------------|-----------------|
| Happy | Rachel | Bright, cheerful |
| Sad | Bella | Soft, gentle |
| Angry | Josh | Strong, assertive |
| Fear | Elli | Cautious, gentle |
| Surprise | Antoni | Energetic, expressive |
| Disgust | Arnold | Neutral, controlled |
| Neutral | Sam | Balanced, natural |

## Testing

### 🎥 Camera Emotion Detection:
```bash
# Start the backend
python main.py

# Open camera test UI in browser
open camera_test_ui.html
```

### 🧪 Comprehensive Testing:
```bash
# Test all API endpoints
python test_client.py
```

### 🌐 Interactive Web Testing:
1. **Camera Test UI** (`camera_test_ui.html`):
   - Live camera feed with real-time emotion detection
   - Stable emotion analysis with 1-second intervals
   - Statistics and detection logs
   
2. **Full Test UI** (`test_ui.html`):
   - Complete API testing interface
   - Voice agent testing with ElevenLabs TTS
   - WebSocket streaming integration
   
3. **WebSocket Test** (`websocket_test.html`):
   - Real-time emotion streaming
   - Connection management

### 📡 API Endpoints:
- `GET /health` - System status and camera info
- `GET /current_emotion` - Current detected emotion
- `GET /start_emotion_stream` - Server-sent events stream
- `GET /ws/emotions` - WebSocket endpoint for real-time updates
- `POST /analyze_frame` - Process camera frames from browser
- `POST /talk` - Generate speech from text with emotion mapping
- `GET /emotions/available` - List available emotions and voice mappings

## 🎯 Project Status

### ✅ Production Ready
- **🌐 Cloud Deployment**: Successfully deployed to Google Cloud Run
- **🔧 Modular Architecture**: Professional backend structure with service separation
- **🎭 Emotion Engine**: Real-time facial emotion detection with stability algorithms
- **🗣️ Voice Synthesis**: ElevenLabs integration with emotion-mapped voices
- **🤖 AI Conversations**: GPT-4o powered intelligent responses
- **📱 Web Interface**: Modern HTML5/JavaScript frontend with camera integration
- **🔄 Real-Time Streaming**: WebSocket and SSE support for live updates
- **📊 Session Management**: Persistent user context and conversation tracking

### 🏆 Recent Achievements
- **Production Deployment**: Fully operational on Google Cloud Run
- **Internationalization**: Complete translation from Chinese to English
- **Code Cleanup**: Removed all legacy/obsolete files for clean codebase
- **Architecture Refactor**: Implemented professional modular backend structure
- **Performance Optimization**: Enhanced emotion stability and detection accuracy

### 🔧 Technical Highlights
- **Docker Containerization**: Multi-architecture support (amd64/linux)
- **Auto-Scaling**: 0-10 instances based on demand
- **Health Monitoring**: Comprehensive endpoint monitoring and logging
- **CORS Configuration**: Proper browser integration support
- **Error Handling**: Robust exception management and user feedback

## 📋 Requirements

### System Requirements
- **Python**: 3.12+ (recommended for optimal performance)
- **Package Manager**: `uv` for fast dependency management
- **Hardware**: Webcam access for emotion detection
- **Network**: Internet connection for AI services

### API Keys (Required for Full Functionality)
- **ElevenLabs API**: Voice synthesis and TTS generation
- **OpenAI API**: GPT-4o for intelligent conversations

### Development Tools
- **Docker**: For containerization and deployment
- **Google Cloud SDK**: For cloud deployment (optional)
- **Modern Browser**: Chrome/Firefox/Safari for web interface

## Usage Examples

### Get Current Emotion
```bash
curl http://localhost:8000/current_emotion
```

### Generate Speech
```bash
curl -X POST "http://localhost:8000/talk" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! How are you feeling today?", "emotion": "happy"}'
```

### WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/emotions');
ws.onmessage = function(event) {
    const emotionData = JSON.parse(event.data);
    console.log('Current emotion:', emotionData.emotion);
};
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **OpenCV** - Computer vision and webcam processing
- **FER** - Facial emotion recognition library
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment

### AI & Machine Learning
- **OpenAI GPT-4o** - Advanced language model for conversations
- **TensorFlow** - ML backend for emotion detection
- **NumPy** - Numerical computing for image processing

### Voice & Audio
- **ElevenLabs API** - Premium text-to-speech synthesis
- **Base64 Audio** - Efficient audio data transmission

### Real-Time Communication
- **WebSockets** - Bidirectional real-time communication
- **Server-Sent Events** - Live emotion streaming
- **CORS Middleware** - Cross-origin resource sharing

### Cloud & Deployment
- **Google Cloud Run** - Serverless container platform
- **Docker** - Containerization and deployment
- **Google Container Registry** - Container image storage

### Frontend
- **HTML5** - Modern web standards
- **JavaScript ES6+** - Interactive user interface
- **WebRTC** - Browser camera access

## 📝 Important Notes

### 🎥 Camera & Emotion Detection
- Camera initializes automatically on server startup
- Emotion detection runs continuously with 1-second intervals
- Stability algorithm prevents rapid emotion changes (3-5 second persistence)
- Supports both browser camera integration and direct webcam access

### 🗣️ Voice Generation
- Requires active internet connection for ElevenLabs API
- Valid API key needed for voice synthesis
- Emotion-to-voice mapping provides contextually appropriate responses
- Audio returned as base64 for easy web integration

### 🌐 Deployment
- Production service available at Google Cloud Run
- Auto-scaling handles traffic spikes automatically
- Health endpoints provide system status monitoring
- CORS configured for browser-based applications

### 🔧 Development
- Use `camera_test_ui.html` for local testing
- WebSocket endpoints available for real-time integration
- Comprehensive API documentation at `/docs` endpoint
- Session management maintains conversation context

---

**Built with ❤️ for the Pond Hackathon**

*# 🎭 EmoHunter

**Emotionally-aware AI companion with real-time facial emotion detection, Apple Watch biometric integration, voice interaction, and intelligent conversation generation.**

EmoHunter combines cutting-edge computer vision, Apple Watch biometric data analysis, natural language processing, and voice synthesis to create an AI that truly understands and responds to human emotions through multiple data sources including facial expressions, physiological signals, and conversational context.*
