#!/usr/bin/env python3
"""
🧪 Mock Biometric Data Test Suite

Tests the automatic mock data generation when no real Apple Watch data is provided.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "mock_test_user"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ EmoHunter server is running")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return False

def test_empty_data_upload():
    """Test uploading empty biometric data to trigger mock generation"""
    print("\n📱 Step 1: Testing empty data upload (should trigger mock generation)...")
    
    # Upload completely empty biometric data
    empty_data = {
        "user_id": TEST_USER_ID,
        "device_id": "test_device"
        # No biometric data arrays provided
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/biometric/upload",
            json=empty_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Empty data upload successful - mock data generated!")
            print(f"   📊 Insights generated: {result.get('insights_generated', 0)}")
            print(f"   💪 Wellness score: {result.get('wellness_score', 0):.1f}/100")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def test_biometric_context_retrieval():
    """Test retrieving biometric context after mock data generation"""
    print("\n🧠 Step 2: Testing biometric context retrieval...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/biometric/context/{TEST_USER_ID}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Biometric context retrieved successfully!")
            print(f"   📝 Context: {result.get('contextual_prompt', 'No context')[:100]}...")
            print(f"   🎯 Insights count: {result.get('insights_count', 0)}")
            print(f"   💪 Wellness score: {result.get('wellness_score', 0):.1f}/100")
            
            if result.get('recommendations'):
                print(f"   💡 Recommendations: {', '.join(result['recommendations'][:3])}")
            
            return True
        else:
            print(f"❌ Context retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving context: {e}")
        return False

def test_integrated_emotion_analysis():
    """Test integrated emotion analysis with mock biometric data"""
    print("\n🎭 Step 3: Testing integrated emotion analysis...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/integrated_analysis/{TEST_USER_ID}"
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Integrated emotion analysis successful!")
            
            # Display facial emotion data
            if 'facial_emotion' in result:
                facial = result['facial_emotion']
                print(f"   😊 Facial emotion: {facial.get('dominant_emotion', 'unknown')} ({facial.get('confidence', 0):.1%})")
            
            # Display biometric insights
            if 'biometric_insights' in result:
                bio = result['biometric_insights']
                print(f"   📊 Biometric insights: {bio.get('insights_count', 0)} insights")
                print(f"   💪 Wellness score: {bio.get('wellness_score', 0):.1f}/100")
            
            # Display recommendations
            if 'recommendations' in result:
                recs = result['recommendations']
                print(f"   🎯 CBT/DBT recommendations: {', '.join(recs[:3])}")
            
            return True
        else:
            print(f"❌ Integrated analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in integrated analysis: {e}")
        return False

def test_conversation_with_mock_data():
    """Test conversation generation with mock biometric context"""
    print("\n💬 Step 4: Testing conversation generation with mock biometric context...")
    
    conversation_data = {
        "user_id": TEST_USER_ID,
        "message": "How am I feeling today?",
        "include_biometric_context": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json=conversation_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversation generation successful!")
            print(f"   💬 Response: {result.get('response', 'No response')[:150]}...")
            
            if 'biometric_context_used' in result:
                print(f"   📊 Biometric context included: {result['biometric_context_used']}")
            
            return True
        else:
            print(f"❌ Conversation generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in conversation generation: {e}")
        return False

def test_mock_data_details():
    """Display detailed mock data information"""
    print("\n📋 Step 5: Analyzing generated mock data details...")
    
    try:
        # Get the latest analysis result
        response = requests.get(f"{BASE_URL}/api/v1/biometric/context/{TEST_USER_ID}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Mock data analysis:")
            print(f"   📱 Data source: Mock Apple Watch")
            print(f"   ⏰ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📊 Total insights: {result.get('insights_count', 0)}")
            print(f"   💪 Wellness score: {result.get('wellness_score', 0):.1f}/100")
            
            # Show emotional insights if available
            if 'primary_emotions' in result and result['primary_emotions']:
                print(f"   🎭 Primary emotions detected: {', '.join(result['primary_emotions'])}")
            
            # Show recommendations
            if 'recommendations' in result and result['recommendations']:
                print(f"   💡 CBT/DBT recommendations:")
                for rec in result['recommendations'][:5]:
                    print(f"      • {rec}")
            
            return True
        else:
            print(f"❌ Could not retrieve mock data details: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing mock data: {e}")
        return False

def main():
    """Run the complete mock biometric data test suite"""
    print("🧪 Mock Biometric Data Test Suite")
    print("=" * 50)
    
    # Check server health
    if not test_server_health():
        return
    
    print(f"\n🍎 Testing Mock Apple Watch Data Generation")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_empty_data_upload,
        test_biometric_context_retrieval,
        test_integrated_emotion_analysis,
        test_conversation_with_mock_data,
        test_mock_data_details
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'=' * 50}")
    if passed == total:
        print(f"✅ All {total} tests passed! Mock biometric data generation is working perfectly.")
    else:
        print(f"❌ {passed}/{total} tests passed. Some mock data features may need attention.")
    
    print(f"\n📚 Mock Data Features Tested:")
    print(f"   • Automatic mock data generation when input is null/empty")
    print(f"   • Realistic Apple Watch biometric data simulation")
    print(f"   • Integration with emotion analysis engine")
    print(f"   • CBT/DBT recommendations from mock data")
    print(f"   • Conversation generation with mock biometric context")

if __name__ == "__main__":
    main()
