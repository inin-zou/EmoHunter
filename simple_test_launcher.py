#!/usr/bin/env python3
"""
🎭 EmoHunter Simple Test Launcher
Quickly start simulation services for UI testing
"""

import time
import random
import webbrowser
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
import threading
import io
import base64
from PIL import Image
import numpy as np
import os
import requests
import json

# Try to import OpenCV and FER
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not installed, will use simulation mode")

try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError:
    FER_AVAILABLE = False
    print("⚠️ FER library not installed, will use simulation mode")

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ElevenLabs API URLs
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"
ELEVENLABS_VOICES_URL = "https://api.elevenlabs.io/v1/voices"

# Default voice ID (Rachel)
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Create FastAPI application
app = FastAPI(title="EmoHunter Test Server", description="Simulation server for all microservices")

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FER detector
emotion_detector = None
if FER_AVAILABLE and OPENCV_AVAILABLE:
    try:
        emotion_detector = FER(mtcnn=True)
        print("✅ FER emotion detector initialized successfully")
    except Exception as e:
        print(f"⚠️ FER initialization failed: {e}")
        emotion_detector = None

# Simulated session storage
sessions = {}
current_session_id = f"session_{int(time.time())}"

@app.get("/")
async def root():
    return {"message": "🎭 EmoHunter test server running", "services": ["emotion", "conversation", "gateway"]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": time.time()}

# New: Image emotion analysis endpoint
@app.post("/analyze_emotion")
async def analyze_emotion_from_image(image: UploadFile = File(...)):
    """Analyze emotions in uploaded image"""
    try:
        # Read image data
        image_data = await image.read()
        
        if emotion_detector and OPENCV_AVAILABLE:
            # Use real FER detection
            try:
                # Convert image data to OpenCV format
                nparr = np.frombuffer(image_data, np.uint8)
                cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if cv_image is None:
                    raise ValueError("Unable to decode image")
                
                # Use FER to detect emotions
                result = emotion_detector.detect_emotions(cv_image)
                
                if result and len(result) > 0:
                    emotions = result[0]['emotions']
                    dominant_emotion = max(emotions, key=emotions.get)
                    confidence = emotions[dominant_emotion]
                    
                    return {
                        "emotion": dominant_emotion,
                        "confidence": confidence,
                        "all_emotions": emotions,
                        "faces_detected": len(result),
                        "method": "FER_real",
                        "timestamp": time.time()
                    }
                else:
                    # No face detected, return neutral emotion
                    return {
                        "emotion": "neutral",
                        "confidence": 0.5,
                        "all_emotions": {"neutral": 0.5},
                        "faces_detected": 0,
                        "method": "FER_no_face",
                        "timestamp": time.time()
                    }
                    
            except Exception as e:
                print(f"FER detection failed: {e}")
                # Fall back to simulation mode
                pass
        
        # Simulate emotion detection
        emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
        weights = [0.2, 0.15, 0.1, 0.1, 0.15, 0.1, 0.2]  # Give higher weight to happy and neutral
        
        emotion = random.choices(emotions, weights=weights)[0]
        confidence = 0.6 + random.random() * 0.3
        
        # Generate scores for all emotions
        all_emotions = {}
        remaining_confidence = 1.0 - confidence
        for e in emotions:
            if e == emotion:
                all_emotions[e] = confidence
            else:
                all_emotions[e] = remaining_confidence * random.random() / (len(emotions) - 1)
        
        return {
            "emotion": emotion,
            "confidence": confidence,
            "all_emotions": all_emotions,
            "faces_detected": 1,
            "method": "simulated",
            "timestamp": time.time()
        }
        
    except Exception as e:
        print(f"Image analysis error: {e}")
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "all_emotions": {"neutral": 0.5},
            "faces_detected": 0,
            "method": "error_fallback",
            "error": str(e),
            "timestamp": time.time()
        }

# Emotion analysis engine endpoints (port 8001 simulation)
@app.get("/current_emotion")
async def get_current_emotion():
    """Get current emotion"""
    emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
    emotion = random.choice(emotions)
    confidence = 0.6 + random.random() * 0.3
    
    return {
        "emotion": emotion,
        "confidence": confidence,
        "timestamp": time.time(),
        "status": "detected"
    }

@app.post("/start_emotion_stream")
async def start_emotion_stream():
    """Start emotion detection stream"""
    return {"status": "started", "message": "Emotion detection started"}

@app.post("/stop_emotion_stream") 
async def stop_emotion_stream():
    """Stop emotion detection stream"""
    return {"status": "stopped", "message": "Emotion detection stopped"}

# Conversation engine endpoints (port 8002 simulation)
@app.post("/generate")
async def generate_conversation(request: dict):
    """Generate context-aware conversation response"""
    message = request.get("message", "")
    emotion_context = request.get("emotion_context", "neutral")
    session_id = request.get("session_id", current_session_id)
    user_id = request.get("user_id", "default_user")
    
    # Initialize session storage
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [], 
            "emotions": [],
            "user_id": user_id,
            "created_at": time.time()
        }
    
    # Get conversation history
    conversation_history = sessions[session_id]["messages"]
    
    # Use OpenAI GPT-4o to generate response
    if OPENAI_API_KEY:
        try:
            ai_response = await generate_gpt_response(message, emotion_context, conversation_history)
        except Exception as e:
            print(f"GPT generation failed, using simulated response: {e}")
            ai_response = generate_fallback_response(message, emotion_context, conversation_history)
    else:
        ai_response = generate_fallback_response(message, emotion_context, conversation_history)
    
    # Save conversation to session
    sessions[session_id]["messages"].append({
        "user": message,
        "ai": ai_response,
        "emotion": emotion_context,
        "timestamp": time.time()
    })
    
    if emotion_context not in sessions[session_id]["emotions"]:
        sessions[session_id]["emotions"].append(emotion_context)
    
    return {
        "response": ai_response,
        "emotion_context": emotion_context,
        "session_id": session_id,
        "context_used": len(conversation_history) > 0,
        "history_length": len(conversation_history)
    }

async def generate_gpt_response(message: str, emotion_context: str, conversation_history: list) -> str:
    """Use OpenAI GPT-4o to generate context-aware response"""
    import openai
    
    # Build system prompt
    system_prompt = """You are Aura, an emotionally intelligent AI mental health companion.

Your core principles:
- Provide compassionate, non-judgmental support using CBT and DBT techniques
- Adjust your tone and approach based on the user's emotional state
- You are not a licensed therapist, but a supportive mental health companion
- Help users understand their emotions and develop healthy coping strategies
- Encourage seeking professional help when appropriate

Emotion-based response guidelines:
- Happy: Warm encouragement, celebrate their positive state
- Sad: Use gentle, soft language; validate their feelings; provide comfort
- Angry: Stay calm and stable; help them handle anger constructively
- Fear: Be reassuring and stable; help them feel safe and supported
- Surprise: Match their energy appropriately; help them process new information
- Disgust: Be understanding; help them process negative emotions
- Neutral: Be balanced and supportive; check on their wellbeing

Always:
- Keep responses conversational and warm (usually 2-3 sentences)
- Use "I" statements to express empathy
- Ask gentle follow-up questions when appropriate
- Validate their emotional experience
- Maintain professional boundaries while providing support
"""
    
    # Build conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (last 10 exchanges)
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    for msg in recent_history:
        messages.append({"role": "user", "content": msg["user"]})
        messages.append({"role": "assistant", "content": msg["ai"]})
    
    # Add current message with emotion context
    current_message = f"[Current emotion: {emotion_context}] {message}"
    messages.append({"role": "user", "content": current_message})
    
    # Call OpenAI API
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

def generate_fallback_response(message: str, emotion_context: str, conversation_history: list) -> str:
    """Generate simulated context-aware response"""
    # Check if there's conversation history
    has_context = len(conversation_history) > 0
    
    if has_context:
        # Get recent conversation
        last_exchange = conversation_history[-1]
        last_user_msg = last_exchange["user"]
        
        # Context-aware response templates
        context_responses = {
            "happy": [
                f"I'm glad you continue to maintain a positive attitude! You mentioned '{last_user_msg}' earlier, and now about '{message}', I can feel your happiness continuing.",
                f"Seeing you go from '{last_user_msg}' to now '{message}', your cheerful mood is really infectious!",
                f"Continuing our earlier conversation about '{last_user_msg}', what you're saying now about '{message}' makes me even happier for you!"
            ],
            "sad": [
                f"I notice that from our earlier discussion about '{last_user_msg}' to now '{message}', your emotions seem somewhat heavy. I'm here to accompany you.",
                f"Combining what you mentioned earlier about '{last_user_msg}' and now '{message}', I can sense the complex emotions in your heart.",
                f"From '{last_user_msg}' to '{message}', I see the change in your emotions, please know you're not alone in facing these."
            ],
            "neutral": [
                f"Based on our earlier discussion about '{last_user_msg}', what you're mentioning now about '{message}' gives me some new perspectives.",
                f"From '{last_user_msg}' to '{message}', I see the natural continuation of our topic, let's continue exploring deeper.",
                f"Combining what you said earlier about '{last_user_msg}', your current '{message}' adds new dimensions to our conversation."
            ]
        }
    else:
        # First conversation response templates
        context_responses = {
            "happy": [
                f"Nice to meet you! I can feel your positive energy. About '{message}', I'd love to share this happiness with you!",
                f"Welcome! Your cheerful mood is infectious. '{message}' sounds great, tell me more!"
            ],
            "sad": [
                f"Hello, I notice your current emotional state. About '{message}', I want you to know I'm here to listen and support you.",
                f"Thank you for sharing with me. '{message}' does sound emotionally heavy, let's talk about it slowly together."
            ],
            "neutral": [
                f"Hello! Nice to have a conversation with you. About '{message}', I'm interested to hear your thoughts.",
                f"Welcome! '{message}' is an interesting start, let's explore it deeper."
            ]
        }
    
    # Choose appropriate response
    responses = context_responses.get(emotion_context, context_responses["neutral"])
    return random.choice(responses)

# ElevenLabs STT endpoints
@app.post("/speech_to_text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Use ElevenLabs to convert speech to text"""
    try:
        if not ELEVENLABS_API_KEY:
            # Simulation mode
            return {
                "text": "This is simulated speech recognition result, please set ELEVENLABS_API_KEY environment variable",
                "method": "simulated",
                "confidence": 0.95
            }
        
        # Read audio data
        audio_data = await audio.read()
        
        # Call ElevenLabs STT API
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Ensure correct audio format
        files = {
            "audio": ("audio.wav", audio_data, "audio/wav")
        }
        
        # Add model parameters
        data = {
            "model_id": "eleven_multilingual_v2"
        }
        
        response = requests.post(ELEVENLABS_STT_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("text", ""),
                "method": "elevenlabs",
                "confidence": 0.95
            }
        else:
            raise Exception(f"ElevenLabs STT API error: {response.status_code}")
            
    except Exception as e:
        print(f"STT error: {e}")
        # Fall back to simulation mode
        return {
            "text": "Speech recognition failed, this is simulated result",
            "method": "error_fallback",
            "error": str(e),
            "confidence": 0.5
        }

# ElevenLabs TTS endpoints
@app.post("/text_to_speech")
async def text_to_speech(request: dict):
    """Use ElevenLabs to convert text to speech"""
    try:
        text = request.get("text", "")
        emotion = request.get("emotion", "neutral")
        voice_id = request.get("voice_id", DEFAULT_VOICE_ID)
        
        if not ELEVENLABS_API_KEY:
            # Simulation mode
            return {
                "status": "simulated",
                "text": text,
                "emotion": emotion,
                "audio_available": False,
                "message": "Please set the ELEVENLABS_API_KEY environment variable to enable real speech synthesis"
            }
        
        # Adjust voice parameters based on emotion
        voice_settings = {
            "stability": 0.7,
            "similarity_boost": 0.8,
            "style": 0.5,
            "use_speaker_boost": True
        }
        
        # Use consistent voice settings for all emotions
        # Single voice configuration for simplicity
        
        # Call ElevenLabs TTS API
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "voice_settings": voice_settings
        }
        
        tts_url = f"{ELEVENLABS_TTS_URL}/{voice_id}"
        response = requests.post(tts_url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Return audio data
            return Response(
                content=response.content,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=speech.mp3",
                    "X-Emotion": emotion,
                    "X-Voice-ID": voice_id
                }
            )
        else:
            raise Exception(f"ElevenLabs TTS API error: {response.status_code}")
            
    except Exception as e:
        print(f"TTS error: {e}")
        return {
            "status": "error",
            "text": text,
            "emotion": emotion,
            "audio_available": False,
            "error": str(e),
            "message": "Speech synthesis failed"
        }

@app.post("/synthesize")
async def synthesize_speech(request: dict):
    """Speech synthesis (compatibility endpoint)"""
    # Forward to new TTS endpoint
    return await text_to_speech(request)

# Complete voice conversation endpoint
@app.post("/api/v1/voice_conversation")
async def voice_conversation(audio: UploadFile = File(...), session_id: str = None, user_id: str = "voice_user"):
    """
    Complete voice conversation workflow:
    1. ElevenLabs STT: Speech to text
    2. Camera emotion detection
    3. OpenAI GPT-4o: Emotion-aware conversation generation
    4. ElevenLabs TTS: Text to speech
    """
    try:
        # Step 1: Speech to text
        stt_result = await speech_to_text(audio)
        user_message = stt_result.get("text", "")
        
        if not user_message.strip():
            return {
                "error": "Speech recognition failed or empty",
                "stt_result": stt_result
            }
        
        # Step 2: Get current emotion
        emotion_data = await get_current_emotion()
        detected_emotion = emotion_data["emotion"]
        
        # Step 3: Generate conversation response
        if not session_id:
            session_id = f"voice_session_{int(time.time())}"
        
        conversation_request = {
            "message": user_message,
            "emotion_context": detected_emotion,
            "session_id": session_id,
            "user_id": user_id
        }
        
        conversation_response = await generate_conversation(conversation_request)
        ai_response = conversation_response["response"]
        
        # Step 4: Text to speech
        tts_request = {
            "text": ai_response,
            "emotion": detected_emotion
        }
        
        # Check if ElevenLabs API key is available
        if ELEVENLABS_API_KEY:
            # Return complete voice conversation result
            tts_response = await text_to_speech(tts_request)
            
            # If TTS successful, return audio stream
            if isinstance(tts_response, Response):
                # Use ASCII encoding to handle Chinese headers
                safe_user_message = user_message.encode('ascii', 'ignore').decode('ascii') if user_message else 'voice_input'
                safe_ai_response = ai_response.encode('ascii', 'ignore').decode('ascii') if ai_response else 'ai_response'
                
                return Response(
                    content=tts_response.body,
                    media_type="audio/mpeg",
                    headers={
                        "X-User-Message": safe_user_message,
                        "X-AI-Response": safe_ai_response,
                        "X-Detected-Emotion": detected_emotion,
                        "X-Session-ID": session_id,
                        "X-STT-Method": stt_result.get("method", "unknown"),
                        "Content-Disposition": "attachment; filename=voice_response.mp3"
                    }
                )
        
        # If no API key or TTS failed, return JSON result
        return {
            "user_message": user_message,
            "ai_response": ai_response,
            "detected_emotion": detected_emotion,
            "session_id": session_id,
            "stt_result": stt_result,
            "tts_available": bool(ELEVENLABS_API_KEY),
            "context_used": conversation_response["context_used"],
            "timestamp": time.time()
        }
        
    except Exception as e:
        print(f"Voice conversation error: {e}")
        return {
            "error": str(e),
            "message": "Voice conversation processing failed",
            "timestamp": time.time()
        }

# API Gateway endpoints (port 8000 simulation)
@app.post("/api/v1/unified/emotion_chat")
async def unified_emotion_chat(request: dict):
    """Unified emotion-aware conversation endpoint"""
    message = request.get("message", "")
    user_id = request.get("user_id", "test_user")
    session_id = request.get("session_id", current_session_id)
    emotion_context = request.get("emotion_context", "neutral")
    include_emotion = request.get("include_emotion", True)
    include_voice = request.get("include_voice", False)
    use_session_context = request.get("use_session_context", True)
    
    # If emotion detection is enabled, get current emotion
    if include_emotion:
        emotion_data = await get_current_emotion()
        detected_emotion = emotion_data["emotion"]
    else:
        detected_emotion = emotion_context
    
    # Generate conversation response
    conversation_request = {
        "message": message,
        "emotion_context": detected_emotion,
        "session_id": session_id,
        "user_id": user_id
    }
    
    conversation_response = await generate_conversation(conversation_request)
    
    # Build unified response
    result = {
        "ai_response": conversation_response["response"],
        "detected_emotion": detected_emotion,
        "session_id": session_id,
        "user_id": user_id,
        "context_used": conversation_response["context_used"],
        "timestamp": time.time()
    }
    
    # If speech synthesis is enabled
    if include_voice:
        voice_response = await synthesize_speech({
            "text": conversation_response["response"],
            "emotion": detected_emotion
        })
        result["voice_synthesis"] = voice_response
    
    # Add session context information
    if use_session_context and session_id in sessions:
        session_data = sessions[session_id]
        result["session_context"] = {
            "message_count": len(session_data["messages"]),
            "emotions_detected": session_data["emotions"],
            "session_duration": time.time() - session_data["messages"][0]["timestamp"] if session_data["messages"] else 0
        }
    
    return result

# Session management endpoints
@app.post("/api/v1/session/create")
async def create_session(request: dict):
    """Create new session"""
    user_id = request.get("user_id", "test_user")
    new_session_id = f"session_{user_id}_{int(time.time())}"
    
    sessions[new_session_id] = {
        "user_id": user_id,
        "created_at": time.time(),
        "messages": [],
        "emotions": []
    }
    
    return {
        "session_id": new_session_id,
        "status": "created",
        "user_id": user_id
    }

@app.get("/api/v1/session/{session_id}/context")
async def get_session_context(session_id: str):
    """Get session context"""
    if session_id not in sessions:
        return {"error": "Session not found"}
    
    session_data = sessions[session_id]
    return {
        "session_id": session_id,
        "message_count": len(session_data["messages"]),
        "emotions_detected": session_data["emotions"],
        "created_at": session_data.get("created_at", time.time()),
        "last_activity": session_data["messages"][-1]["timestamp"] if session_data["messages"] else session_data.get("created_at", time.time())
    }

@app.get("/api/v1/session/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 10):
    """Get conversation history"""
    if session_id not in sessions:
        return []
    
    messages = sessions[session_id]["messages"]
    return messages[-limit:] if limit else messages

def open_camera_ui():
    """Open camera test UI"""
    time.sleep(3)  # Wait for service to start
    ui_path = Path(__file__).parent / "camera_test_ui.html"
    
    if ui_path.exists():
        print(f"🌐 Automatically opening camera test UI...")
        webbrowser.open(f"file://{ui_path.absolute()}")
    else:
        print("❌ Camera test UI file not found")

def main():
    """Main function"""
    print("🎭" + "="*50 + "🎭")
    print("🚀 EmoHunter Camera Test Launcher")
    print("   Integrated simulation server - Port 8000")
    print("🎭" + "="*50 + "🎭")
    print()
    
    print("📋 Simulation services:")
    print("  ✅ Emotion analysis engine - /current_emotion")
    print("  ✅ Image emotion analysis - /analyze_emotion") 
    print("  ✅ ElevenLabs STT - /speech_to_text")
    print("  ✅ ElevenLabs TTS - /text_to_speech")
    print("  ✅ Complete voice conversation - /api/v1/voice_conversation")
    print("  ✅ Conversation engine - /generate") 
    print("  ✅ API Gateway - /api/v1/unified/emotion_chat")
    print("  ✅ Session management - /api/v1/session/*")
    print()
    
    print("🔧 Detection capabilities:")
    if FER_AVAILABLE and OPENCV_AVAILABLE:
        print("  ✅ Real FER emotion detection")
    else:
        print("  ⚠️ Simulated emotion detection (FER/OpenCV not installed)")
    
    print("🎤 Voice capabilities:")
    if ELEVENLABS_API_KEY:
        print("  ✅ ElevenLabs STT/TTS (real voice)")
    else:
        print("  ⚠️ Simulated voice (please set ELEVENLABS_API_KEY)")
    
    if OPENAI_API_KEY:
        print("  ✅ OpenAI GPT-4o (real conversation)")
    else:
        print("  ⚠️ Simulated conversation (please set OPENAI_API_KEY)")
    print()
    
    # Open UI in background thread
    ui_thread = threading.Thread(target=open_camera_ui)
    ui_thread.daemon = True
    ui_thread.start()
    
    print("🌐 Service address: http://localhost:8000")
    print("📱 Camera test UI will open automatically...")
    print("💡 Press Ctrl+C to stop service")
    print()
    
    try:
        # Start server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
