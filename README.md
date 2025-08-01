# EmoHunter - FastAPI Backend for Real-Time Emotion Detection and Voice Agent

A FastAPI backend that provides real-time facial emotion detection from webcam and emotionally appropriate voice responses using ElevenLabs API.

## Features

🎥 **Real-Time Emotion Detection**
- Captures video from webcam using OpenCV
- Processes frames using the `fer` library for emotion detection (with mock fallback)
- Provides continuous emotion updates via REST API or WebSocket
- **Note**: Currently using mock emotion detection due to FER library compatibility issues

🗣️ **Voice Agent (TTS)**
- Maps detected emotions to appropriate ElevenLabs voice styles
- Generates emotionally appropriate speech responses
- Returns audio as base64 for easy integration
- **Note**: Requires ElevenLabs API key configuration

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

1. **Create Virtual Environment with uv**
   ```bash
   # Remove old venv if it exists
   rm -rf venv
   
   # Create new virtual environment with uv
   uv venv
   
   # Activate the virtual environment
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   # Install dependencies using uv (faster than pip)
   uv pip install -r requirements.txt
   ```

3. **Configure ElevenLabs API (Optional)**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env and add your ElevenLabs API key
   # ELEVENLABS_API_KEY=your_api_key_here
   ```

4. **Run the Server**
   ```bash
   # Make sure virtual environment is activated
   source .venv/bin/activate
   
   # Start the FastAPI server
   python main.py
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Current Emotion: http://localhost:8000/current_emotion

6. **Test the API**
   ```bash
   # Run the test client to validate all endpoints
   source .venv/bin/activate
   python test_client.py
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

## Current Status

### ✅ Working Features:
- **FastAPI Backend**: Running on http://localhost:8000 with CORS support
- **Real Camera Integration**: Browser camera frames sent to backend for analysis
- **Stable Emotion Detection**: Improved stability logic prevents rapid emotion changes
- **All API Endpoints**: Fully functional and tested
- **WebSocket Streaming**: Real-time emotion updates
- **Interactive Test UIs**: 
  - `camera_test_ui.html` - Live camera emotion detection
  - `test_ui.html` - Full API testing interface
  - `websocket_test.html` - WebSocket streaming test
- **Python Test Client**: Comprehensive API validation script
- **ElevenLabs Integration**: Voice agent with emotion-based TTS (requires API key)

### 🎯 Recent Improvements:
- **CORS Middleware**: Fixed browser "Failed to fetch" issues
- **Camera Frame Processing**: Real browser camera frames sent to `/analyze_frame` endpoint
- **Emotion Stability**: Added consistency logic to prevent rapid emotion changes
- **Detection Frequency**: Optimized from 500ms to 1000ms for realistic behavior
- **Mock Detection Enhancement**: 70% stability bias for more realistic demo behavior

### ⚠️ Known Issues:
- **FER Library Compatibility**: `moviepy.editor` import error prevents real facial emotion analysis
- **ElevenLabs TTS**: Requires valid API key for voice generation

### 🔧 Current Behavior:
- **Mock Emotion Detection**: Provides realistic demo with stability improvements
- **Camera Integration**: Full end-to-end camera → backend → emotion analysis pipeline working
- **Stable Results**: Emotions persist for 3-5 seconds with natural transitions

## Requirements

- Python 3.12+ (recommended)
- `uv` package manager (for faster dependency management)
- Webcam access (currently functional)
- ElevenLabs API key (optional, for voice generation)
- Internet connection (for ElevenLabs API)

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

## Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **OpenCV** - Computer vision library for webcam access
- **FER** - Facial emotion recognition library
- **ElevenLabs** - Text-to-speech API
- **WebSockets** - Real-time communication
- **TensorFlow** - Machine learning backend for emotion detection

## Notes

- The camera starts automatically when the server launches
- Emotion detection runs continuously in the background
- The API supports both polling and streaming for emotion updates
- Voice generation requires an active internet connection and valid ElevenLabs API key
