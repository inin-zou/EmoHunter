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
- `WebSocket /ws/emotions` - Real-time emotion updates via WebSocket

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
- `GET /health` - Health check and system status

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

## Current Status

### ✅ Working Features
- FastAPI server running successfully
- Health check endpoint
- Available emotions endpoint
- Mock emotion detection (random emotions for demo)
- API documentation at `/docs`
- WebSocket support for real-time updates

### ⚠️ Known Issues
- **FER Library**: Real emotion detection disabled due to `moviepy.editor` import issues
- **Camera Access**: Camera initialization fails due to FER library issues
- **ElevenLabs TTS**: Voice generation may fail due to API version compatibility

### 🔧 Workarounds
- Mock emotion detection provides random emotions for testing
- All API endpoints are functional for development/testing
- Voice generation works if ElevenLabs API key is properly configured

## Requirements

- Python 3.12+ (recommended)
- `uv` package manager (for faster dependency management)
- Webcam access (currently not functional due to FER issues)
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
