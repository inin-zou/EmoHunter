# EmoHunter 🎭

**Real-Time Emotion Detection & AI Voice Agent**

A production-ready FastAPI application that combines real-time facial emotion detection with intelligent voice conversations. Built for the Pond Hackathon, EmoHunter creates emotionally-aware AI interactions using computer vision, natural language processing, and voice synthesis.

🌐 **Live Demo**: [https://emohunter-api-6106408799.us-central1.run.app](https://emohunter-api-6106408799.us-central1.run.app)

## 🚀 Production Deployment

**✅ Successfully deployed to Google Cloud Run!**

- **Service URL**: https://emohunter-api-6106408799.us-central1.run.app
- **Status**: Fully operational and production-ready
- **Architecture**: Containerized with Docker, auto-scaling 0-10 instances
- **Resources**: 2GB RAM, 2 CPUs, optimized for real-time processing

## ✨ Key Features

### 🎥 Real-Time Emotion Detection
- **Computer Vision**: OpenCV-powered webcam integration
- **Emotion Analysis**: Advanced facial emotion recognition with FER library
- **Real-Time Streaming**: WebSocket and Server-Sent Events support
- **Stability Engine**: Smart emotion persistence to prevent rapid changes
- **Browser Integration**: Direct camera frame processing from web clients

### 🤖 AI-Powered Voice Agent
- **Emotional Intelligence**: GPT-4o integration for context-aware conversations
- **Voice Synthesis**: ElevenLabs API with emotion-mapped voice selection
- **Session Management**: Persistent conversation context and user tracking
- **Multi-Modal**: Text and audio response generation

### 🏗️ Production Architecture
- **Modular Design**: Clean separation of services and concerns
- **Scalable Backend**: FastAPI with async/await patterns
- **Cloud Native**: Docker containerization with Google Cloud Run deployment
- **API-First**: RESTful endpoints with comprehensive documentation
- **Real-Time Communication**: WebSocket support for live interactions

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

*EmoHunter demonstrates the future of emotionally-aware AI interactions, combining cutting-edge computer vision, natural language processing, and voice synthesis into a seamless user experience.*
