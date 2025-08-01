#!/usr/bin/env python3
"""
Test client for EmoHunter API
Demonstrates how to interact with the emotion detection and voice agent endpoints
"""

import requests
import json
import time
import base64
import websocket
import threading

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_current_emotion():
    """Test getting current emotion"""
    print("\n😊 Testing current emotion detection...")
    try:
        response = requests.get(f"{API_BASE_URL}/current_emotion")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current emotion: {data['emotion']} (confidence: {data['confidence']:.2f})")
            return data['emotion']
        else:
            print(f"❌ Current emotion failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Current emotion error: {e}")
        return None

def test_available_emotions():
    """Test getting available emotions"""
    print("\n📋 Testing available emotions...")
    try:
        response = requests.get(f"{API_BASE_URL}/emotions/available")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available emotions: {', '.join(data['emotions'])}")
            return data
        else:
            print(f"❌ Available emotions failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Available emotions error: {e}")
        return None

def test_voice_agent(text="Hello! This is a test of the voice agent.", emotion=None):
    """Test the voice agent endpoint"""
    print(f"\n🗣️ Testing voice agent with text: '{text}'")
    if emotion:
        print(f"   Using emotion: {emotion}")
    
    try:
        payload = {"text": text}
        if emotion:
            payload["emotion"] = emotion
            
        response = requests.post(f"{API_BASE_URL}/talk", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice generated successfully!")
            print(f"   Text: {data['text']}")
            print(f"   Emotion: {data['emotion']}")
            print(f"   Voice used: {data['voice_used']}")
            print(f"   Audio size: {len(data['audio_base64'])} characters (base64)")
            
            # Optionally save audio to file
            try:
                audio_data = base64.b64decode(data['audio_base64'])
                with open("test_output.mp3", "wb") as f:
                    f.write(audio_data)
                print("   💾 Audio saved as 'test_output.mp3'")
            except Exception as e:
                print(f"   ⚠️ Could not save audio: {e}")
                
            return True
        else:
            print(f"❌ Voice agent failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Voice agent error: {e}")
        return False

def test_websocket_emotions():
    """Test WebSocket emotion streaming"""
    print("\n🔌 Testing WebSocket emotion streaming...")
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if "error" in data:
                print(f"❌ WebSocket error: {data['error']}")
            else:
                print(f"📡 Emotion update: {data['emotion']} (confidence: {data.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"❌ WebSocket message error: {e}")
    
    def on_error(ws, error):
        print(f"❌ WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("🔌 WebSocket connection closed")
    
    def on_open(ws):
        print("✅ WebSocket connection opened")
        # Close after 10 seconds for testing
        def close_after_delay():
            time.sleep(10)
            ws.close()
        threading.Thread(target=close_after_delay, daemon=True).start()
    
    try:
        ws = websocket.WebSocketApp(f"ws://localhost:8000/ws/emotions",
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        ws.run_forever()
        return True
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting EmoHunter API Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Server not available. Make sure the FastAPI server is running.")
        return
    
    # Test available emotions
    test_available_emotions()
    
    # Test current emotion
    current_emotion = test_current_emotion()
    
    # Test voice agent with detected emotion
    if current_emotion:
        test_voice_agent(
            text=f"I can see you're feeling {current_emotion}. That's perfectly normal!",
            emotion=current_emotion
        )
    
    # Test voice agent with different emotions
    emotions_to_test = ["happy", "sad", "angry"]
    for emotion in emotions_to_test:
        test_voice_agent(
            text=f"This is how I sound when responding to {emotion} emotions.",
            emotion=emotion
        )
        time.sleep(1)  # Brief pause between requests
    
    # Test WebSocket (optional - comment out if you don't want to test)
    print("\n" + "=" * 50)
    print("WebSocket test will run for 10 seconds...")
    test_websocket_emotions()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
