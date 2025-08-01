import asyncio
import base64
import cv2
import json
import os
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import numpy as np
# Try to import ElevenLabs with fallback for different API versions
try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_V1 = True
except ImportError:
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import Voice, VoiceSettings
        ELEVENLABS_V1 = False
    except ImportError:
        print("Warning: ElevenLabs library not available. Voice generation will be disabled.")
        ELEVENLABS_V1 = None
from dotenv import load_dotenv
import threading
import time
import random

# Try to import FER, fallback to mock implementation if not available
try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: FER library not available ({e}). Using mock emotion detection.")
    FER_AVAILABLE = False
    
    class MockFER:
        def __init__(self, mtcnn=True):
            self.emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
        
        def detect_emotions(self, frame):
            # Mock emotion detection - returns random emotion for demo
            emotion = random.choice(self.emotions)
            confidence = random.uniform(0.6, 0.95)
            emotions_dict = {e: 0.1 for e in self.emotions}
            emotions_dict[emotion] = confidence
            
            return [{
                'emotions': emotions_dict,
                'box': [100, 100, 200, 200]  # Mock bounding box
            }]
    
    FER = MockFER

# Load environment variables
load_dotenv()

app = FastAPI(title="EmoHunter API", description="Real-time emotion detection and voice agent")

# Global variables for emotion detection
current_emotion = "neutral"
emotion_detector = FER(mtcnn=True)
camera_active = False
cap = None

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if ELEVENLABS_API_KEY and ELEVENLABS_V1:
    set_api_key(ELEVENLABS_API_KEY)
elif ELEVENLABS_API_KEY and ELEVENLABS_V1 is False:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
else:
    elevenlabs_client = None

# Voice style mapping based on emotions
EMOTION_VOICE_MAPPING = {
    "happy": {"voice": "Rachel", "stability": 0.75, "similarity_boost": 0.75},
    "sad": {"voice": "Bella", "stability": 0.30, "similarity_boost": 0.40},
    "angry": {"voice": "Josh", "stability": 0.40, "similarity_boost": 0.60},
    "fear": {"voice": "Elli", "stability": 0.20, "similarity_boost": 0.30},
    "surprise": {"voice": "Antoni", "stability": 0.60, "similarity_boost": 0.70},
    "disgust": {"voice": "Arnold", "stability": 0.50, "similarity_boost": 0.50},
    "neutral": {"voice": "Sam", "stability": 0.50, "similarity_boost": 0.50}
}

class TalkRequest(BaseModel):
    text: str
    emotion: Optional[str] = None

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    timestamp: float

def detect_emotion_from_frame(frame):
    """Detect emotion from a single frame"""
    global current_emotion
    try:
        # Detect emotions
        result = emotion_detector.detect_emotions(frame)
        
        if result:
            # Get the dominant emotion
            emotions = result[0]['emotions']
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion]
            
            # Update global current emotion
            current_emotion = dominant_emotion
            
            return {
                "emotion": dominant_emotion,
                "confidence": confidence,
                "all_emotions": emotions,
                "timestamp": time.time()
            }
    except Exception as e:
        print(f"Error detecting emotion: {e}")
    
    return {
        "emotion": "neutral",
        "confidence": 0.0,
        "all_emotions": {},
        "timestamp": time.time()
    }

def camera_loop():
    """Background camera loop for continuous emotion detection"""
    global cap, camera_active, current_emotion
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    camera_active = True
    print("Camera started for emotion detection")
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Detect emotion from current frame
        emotion_result = detect_emotion_from_frame(frame)
        current_emotion = emotion_result["emotion"]
        
        # Small delay to prevent excessive CPU usage
        time.sleep(0.1)
    
    cap.release()
    print("Camera stopped")

@app.on_event("startup")
async def startup_event():
    """Start camera on application startup"""
    # Start camera in background thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop camera on application shutdown"""
    global camera_active, cap
    camera_active = False
    if cap:
        cap.release()

@app.get("/")
async def root():
    return {"message": "EmoHunter API - Real-time Emotion Detection and Voice Agent"}

@app.get("/current_emotion", response_model=EmotionResponse)
async def get_current_emotion():
    """Get the current detected emotion (simple REST endpoint)"""
    global current_emotion
    
    if not camera_active:
        raise HTTPException(status_code=503, detail="Camera not active")
    
    return EmotionResponse(
        emotion=current_emotion,
        confidence=1.0,  # Simplified for this endpoint
        timestamp=time.time()
    )

@app.get("/start_emotion_stream")
async def start_emotion_stream():
    """Start streaming emotion detection results"""
    global cap, camera_active
    
    if not camera_active:
        raise HTTPException(status_code=503, detail="Camera not available")
    
    def generate_emotion_stream():
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect emotion from current frame
            emotion_result = detect_emotion_from_frame(frame)
            
            # Yield emotion data as JSON
            yield f"data: {json.dumps(emotion_result)}\n\n"
            
            time.sleep(0.5)  # Update every 500ms
    
    return StreamingResponse(
        generate_emotion_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.websocket("/ws/emotions")
async def websocket_emotions(websocket: WebSocket):
    """WebSocket endpoint for real-time emotion streaming"""
    await websocket.accept()
    global cap, camera_active
    
    if not camera_active:
        await websocket.send_json({"error": "Camera not available"})
        await websocket.close()
        return
    
    try:
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect emotion from current frame
            emotion_result = detect_emotion_from_frame(frame)
            
            # Send emotion data via WebSocket
            await websocket.send_json(emotion_result)
            
            await asyncio.sleep(0.5)  # Update every 500ms
            
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})

@app.post("/talk")
async def talk(request: TalkRequest):
    """Generate speech based on text and emotion using ElevenLabs"""
    
    if not ELEVENLABS_API_KEY or ELEVENLABS_V1 is None:
        raise HTTPException(
            status_code=500, 
            detail="ElevenLabs API key not configured or library not available. Please set ELEVENLABS_API_KEY environment variable and install elevenlabs library."
        )
    
    # Use provided emotion or current detected emotion
    emotion = request.emotion or current_emotion
    
    # Get voice configuration for the emotion
    voice_config = EMOTION_VOICE_MAPPING.get(emotion, EMOTION_VOICE_MAPPING["neutral"])
    
    try:
        # Generate audio using ElevenLabs (handle different API versions)
        if ELEVENLABS_V1:
            # Old API version
            audio = generate(
                text=request.text,
                voice=voice_config["voice"],
                model="eleven_monolingual_v1"
            )
        else:
            # New API version
            audio = elevenlabs_client.generate(
                text=request.text,
                voice=Voice(
                    voice_id=voice_config["voice"],
                    settings=VoiceSettings(
                        stability=voice_config["stability"],
                        similarity_boost=voice_config["similarity_boost"]
                    )
                ),
                model="eleven_monolingual_v1"
            )
        
        # Convert audio to base64
        if isinstance(audio, bytes):
            audio_base64 = base64.b64encode(audio).decode('utf-8')
        else:
            # Handle generator or other audio formats
            audio_bytes = b''.join(audio)
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "text": request.text,
            "emotion": emotion,
            "voice_used": voice_config["voice"],
            "audio_base64": audio_base64,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@app.get("/emotions/available")
async def get_available_emotions():
    """Get list of available emotions and their voice mappings"""
    return {
        "emotions": list(EMOTION_VOICE_MAPPING.keys()),
        "voice_mapping": EMOTION_VOICE_MAPPING
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "camera_active": camera_active,
        "current_emotion": current_emotion,
        "elevenlabs_configured": bool(ELEVENLABS_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
