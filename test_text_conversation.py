#!/usr/bin/env python3
"""
🎭 EmoHunter Text Conversation API Test
Test the new text conversation endpoint
"""

import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"
TEXT_CONVERSATION_URL = f"{BASE_URL}/api/v1/text_conversation"

def test_text_conversation():
    """Test the text conversation API"""
    print("🎭 Testing EmoHunter Text Conversation API (Audio Output)")
    print("=" * 50)
    
    # Test cases
    test_messages = [
        {
            "message": "Hello, how are you today?",
            "user_id": "test_user_1"
        },
        {
            "message": "I'm feeling a bit stressed about work",
            "user_id": "test_user_2"
        },
        {
            "message": "Can you help me with some relaxation techniques?",
            "user_id": "test_user_1",
            "session_id": "custom_session_123"
        }
    ]
    
    for i, test_data in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {test_data['message']}")
        print("-" * 40)
        
        try:
            # Send request
            response = requests.post(TEXT_CONVERSATION_URL, json=test_data)
            
            if response.status_code == 200:
                # Check if response is audio or JSON
                content_type = response.headers.get('content-type', '')
                
                if 'audio' in content_type:
                    # Audio response received
                    print(f"✅ Status: Success (Audio Response)")
                    print(f"🎵 Content Type: {content_type}")
                    print(f"🎵 Audio Size: {len(response.content)} bytes")
                    
                    # Extract info from headers
                    user_msg = response.headers.get('X-User-Message', 'N/A')
                    ai_response = response.headers.get('X-AI-Response', 'N/A')
                    emotion = response.headers.get('X-Detected-Emotion', 'N/A')
                    session_id = response.headers.get('X-Session-ID', 'N/A')
                    input_method = response.headers.get('X-Input-Method', 'N/A')
                    
                    print(f"👤 User Message: {user_msg}")
                    print(f"🤖 AI Response: {ai_response}")
                    print(f"😊 Detected Emotion: {emotion}")
                    print(f"🆔 Session ID: {session_id}")
                    print(f"📝 Input Method: {input_method}")
                    
                    # Save audio file for testing
                    audio_filename = f"test_response_{i}.mp3"
                    with open(audio_filename, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 Audio saved as: {audio_filename}")
                    
                else:
                    # JSON response (likely error or fallback)
                    result = response.json()
                    print(f"⚠️ Status: JSON Response (No Audio)")
                    print(f"👤 User Message: {result.get('user_message', 'N/A')}")
                    print(f"🤖 AI Response: {result.get('ai_response', 'N/A')}")
                    print(f"😊 Detected Emotion: {result.get('detected_emotion', 'N/A')}")
                    print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
                    print(f"🔊 TTS Available: {result.get('tts_available', False)}")
                    
                    if 'error' in result:
                        print(f"❌ Error: {result['error']}")
                    
            else:
                print(f"❌ Status: Failed ({response.status_code})")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the EmoHunter server is running on port 8000")
            print("   Run: python simple_test_launcher.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait between requests
        time.sleep(1)

def test_session_continuity():
    """Test session continuity with multiple messages"""
    print("\n\n🔄 Testing Session Continuity")
    print("=" * 50)
    
    session_id = f"continuity_test_{int(time.time())}"
    user_id = "continuity_user"
    
    conversation_flow = [
        "Hi, I'm new here. What can you help me with?",
        "I've been feeling anxious lately",
        "What breathing exercises do you recommend?",
        "Thank you, that was helpful!"
    ]
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"\n💬 Message {i}: {message}")
        print("-" * 30)
        
        try:
            request_data = {
                "message": message,
                "user_id": user_id,
                "session_id": session_id
            }
            
            response = requests.post(TEXT_CONVERSATION_URL, json=request_data)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'audio' in content_type:
                    # Audio response
                    ai_response = response.headers.get('X-AI-Response', 'N/A')
                    emotion = response.headers.get('X-Detected-Emotion', 'N/A')
                    print(f"🤖 Response: {ai_response}")
                    print(f"😊 Emotion: {emotion}")
                    print(f"🎵 Audio Size: {len(response.content)} bytes")
                else:
                    # JSON response
                    result = response.json()
                    print(f"🤖 Response: {result.get('ai_response', 'N/A')}")
                    print(f"😊 Emotion: {result.get('detected_emotion', 'N/A')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
        
        time.sleep(1)

def main():
    """Main test function"""
    print("🚀 Starting EmoHunter Text Conversation API Tests")
    print()
    
    # Basic functionality tests
    test_text_conversation()
    
    # Session continuity tests  
    test_session_continuity()
    
    print("\n\n✅ All tests completed!")
    print("\n📖 API Usage Example:")
    print("""
import requests

# Basic text conversation (returns audio by default)
response = requests.post("http://localhost:8000/api/v1/text_conversation", json={
    "message": "Hello, how are you?",
    "user_id": "my_user"
})

# Check if response is audio or JSON
if 'audio' in response.headers.get('content-type', ''):
    # Audio response - extract info from headers
    ai_response = response.headers.get('X-AI-Response', 'N/A')
    emotion = response.headers.get('X-Detected-Emotion', 'N/A')
    print(f"AI Response: {ai_response}")
    print(f"Detected Emotion: {emotion}")
    
    # Save audio file
    with open('response.mp3', 'wb') as f:
        f.write(response.content)
else:
    # JSON response (fallback)
    result = response.json()
    print(f"AI Response: {result['ai_response']}")
    print(f"Detected Emotion: {result['detected_emotion']}")
""")

if __name__ == "__main__":
    main()
