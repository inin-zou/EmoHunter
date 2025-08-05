#!/usr/bin/env python3
"""
🍎 Apple Watch Integration Test

Test script for Apple Watch biometric data integration with EmoHunter.
Demonstrates how to upload biometric data and get integrated emotional analysis.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "apple_watch_test_user"

def test_apple_watch_simulation():
    """Test Apple Watch data simulation"""
    print("🍎" + "="*50 + "🍎")
    print("🧪 Testing Apple Watch Integration")
    print("🍎" + "="*50 + "🍎")
    print()
    
    # Test 1: Simulate Apple Watch data
    print("📱 Step 1: Simulating Apple Watch data...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/biometric/simulate", 
                               json={"user_id": TEST_USER_ID})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Apple Watch data simulation successful!")
            print(f"   📊 Insights generated: {data['insights_generated']}")
            print(f"   💪 Wellness score: {data['wellness_score']:.1f}/100")
            
            if data.get('insights'):
                print("   🎯 Emotional insights detected:")
                for insight in data['insights']:
                    emotion = insight['emotion_indicator']
                    confidence = insight['confidence']
                    factors = ', '.join(insight['contributing_factors'])
                    print(f"      • {emotion.title()} ({confidence:.1%}) - {factors}")
            
            print(f"   📈 Simulated biometric data:")
            sim_data = data.get('simulated_data', {})
            if 'heart_rate' in sim_data:
                hr = sim_data['heart_rate']
                print(f"      • Heart Rate: {hr['avg_bpm']} bpm (variability: {hr['variability']:.1f})")
            if 'hrv' in sim_data:
                hrv = sim_data['hrv']
                print(f"      • HRV: {hrv['rmssd']:.1f}ms RMSSD (stress: {hrv['stress_score']:.0f}/100)")
            if 'sleep' in sim_data:
                sleep = sim_data['sleep']
                print(f"      • Sleep: {sleep['efficiency']:.1%} efficiency, {sleep['deep_sleep_ratio']:.1%} deep sleep")
            if 'activity' in sim_data:
                activity = sim_data['activity']
                print(f"      • Activity: {activity['steps']} steps, {activity['active_minutes']} active minutes")
            
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
        return False
    
    print()
    
    # Test 2: Get biometric context
    print("🧠 Step 2: Getting biometric context for conversation...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/biometric/context/{TEST_USER_ID}")
        
        if response.status_code == 200:
            context_data = response.json()
            print("✅ Biometric context retrieved successfully!")
            print(f"   📝 Context: {context_data['context']}")
            print(f"   🎯 Insights count: {context_data['insights_count']}")
            print(f"   💪 Wellness score: {context_data['wellness_score']:.1f}/100")
            
            if context_data.get('recommendations'):
                print("   💡 Recommendations:")
                for rec in context_data['recommendations']:
                    print(f"      • {rec}")
        else:
            print(f"❌ Context retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting context: {e}")
        return False
    
    print()
    
    # Test 3: Test integrated emotion analysis
    print("🎭 Step 3: Testing integrated emotion analysis...")
    try:
        # First get current emotion
        response = requests.get(f"{BASE_URL}/current_emotion?user_id={TEST_USER_ID}")
        
        if response.status_code == 200:
            emotion_data = response.json()
            print("✅ Integrated emotion analysis successful!")
            print(f"   😊 Current emotion: {emotion_data['emotion_data']['emotion']}")
            print(f"   🎯 Confidence: {emotion_data['emotion_data']['confidence']:.1%}")
            
            if emotion_data.get('biometric_context'):
                print(f"   🏥 Biometric context: {emotion_data['biometric_context']}")
        else:
            print(f"❌ Emotion analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in emotion analysis: {e}")
        return False
    
    print()
    
    # Test 4: Test conversation with biometric context
    print("💬 Step 4: Testing conversation with biometric context...")
    try:
        conversation_request = {
            "message": "I'm feeling a bit stressed today. How can you help?",
            "user_id": TEST_USER_ID,
            "session_id": f"test_session_{int(time.time())}"
        }
        
        response = requests.post(f"{BASE_URL}/generate", json=conversation_request)
        
        if response.status_code == 200:
            conv_data = response.json()
            print("✅ Biometric-aware conversation successful!")
            print(f"   💬 AI Response: {conv_data['response']}")
            print(f"   🎭 Emotion context: {conv_data.get('emotion_context', 'N/A')}")
        else:
            print(f"❌ Conversation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in conversation: {e}")
        return False
    
    print()
    print("🎉 Apple Watch integration test completed successfully!")
    return True

def test_manual_biometric_upload():
    """Test manual biometric data upload"""
    print("\n📤 Testing manual biometric data upload...")
    
    # Create sample biometric data
    sample_data = {
        "user_id": TEST_USER_ID,
        "heart_rate_data": [
            {"bpm": 85, "timestamp": datetime.now().isoformat(), "context": "resting"},
            {"bpm": 92, "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(), "context": "active"}
        ],
        "sleep_data": [
            {
                "total_sleep_minutes": 420,  # 7 hours
                "sleep_efficiency": 0.75,    # Poor efficiency
                "deep_sleep_minutes": 45,    # Low deep sleep
                "date": (datetime.now() - timedelta(days=1)).date().isoformat()
            }
        ],
        "activity_data": [
            {
                "steps": 2500,  # Low step count
                "active_minutes": 15,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/biometric/upload", json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual biometric upload successful!")
            print(f"   📊 Insights generated: {result['insights_generated']}")
            print(f"   💪 Wellness score: {result['wellness_score']:.1f}/100")
        else:
            print(f"❌ Manual upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in manual upload: {e}")
        return False
    
    return True

def demonstrate_cbt_dbt_integration():
    """Demonstrate CBT/DBT pattern recognition from biometric data"""
    print("\n🧠 Demonstrating CBT/DBT Integration...")
    
    # Simulate different biometric patterns
    test_scenarios = [
        {
            "name": "High Stress Pattern",
            "description": "Elevated HR + Low HRV + Poor Sleep",
            "expected_insights": ["stress", "anxiety"],
            "expected_recommendations": ["deep_breathing", "mindfulness", "stress_management"]
        },
        {
            "name": "Depression Pattern", 
            "description": "Low Activity + Excessive Sleep + Low HR Variability",
            "expected_insights": ["depression", "fatigue"],
            "expected_recommendations": ["behavioral_activation", "gentle_movement"]
        },
        {
            "name": "Fatigue Pattern",
            "description": "Poor Sleep Efficiency + Low Activity",
            "expected_insights": ["fatigue"],
            "expected_recommendations": ["sleep_hygiene", "recovery_techniques"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   🧪 Scenario {i}: {scenario['name']}")
        print(f"      📝 {scenario['description']}")
        
        # Simulate this scenario
        response = requests.post(f"{BASE_URL}/api/v1/biometric/simulate", 
                               json={"user_id": f"test_scenario_{i}"})
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('insights', [])
            
            print(f"      📊 Generated {len(insights)} insights")
            for insight in insights:
                emotion = insight['emotion_indicator']
                confidence = insight['confidence']
                recommendations = insight.get('recommendations', [])
                print(f"         • {emotion.title()} ({confidence:.1%})")
                print(f"           Recommendations: {', '.join(recommendations)}")
        
        time.sleep(1)  # Brief pause between scenarios

def main():
    """Main test function"""
    print("🍎 Apple Watch Integration Test Suite")
    print("=====================================")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ EmoHunter server is not running!")
            print("   Please start the server with: python simple_test_launcher.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to EmoHunter server!")
        print("   Please start the server with: python simple_test_launcher.py")
        return
    
    print("✅ EmoHunter server is running")
    print()
    
    # Run tests
    success = True
    
    # Test 1: Apple Watch simulation
    if not test_apple_watch_simulation():
        success = False
    
    # Test 2: Manual upload
    if not test_manual_biometric_upload():
        success = False
    
    # Test 3: CBT/DBT integration demo
    demonstrate_cbt_dbt_integration()
    
    print("\n" + "="*60)
    if success:
        print("🎉 All Apple Watch integration tests passed!")
        print("\n💡 Next steps:")
        print("   1. Integrate with real Apple Watch using HealthKit")
        print("   2. Add real-time biometric streaming")
        print("   3. Enhance CBT/DBT pattern recognition")
        print("   4. Add biometric-based intervention triggers")
    else:
        print("❌ Some tests failed. Please check the server logs.")
    
    print("\n📚 API Endpoints tested:")
    print("   • POST /api/v1/biometric/simulate")
    print("   • POST /api/v1/biometric/upload") 
    print("   • GET  /api/v1/biometric/context/{user_id}")
    print("   • GET  /current_emotion?user_id={user_id}")
    print("   • POST /generate")

if __name__ == "__main__":
    main()
