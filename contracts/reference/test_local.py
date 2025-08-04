#!/usr/bin/env python3
"""
Local test script for the EmoHunter Incentive Engine

This script tests the incentive engine service locally without requiring
blockchain deployment. It uses mock data to verify the API endpoints work.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List

# Test configuration
TEST_USER_ADDRESS = "0x1234567890123456789012345678901234567890"
BASE_URL = "http://localhost:8001"

class IncentiveEngineLocalTester:
    """Local tester for the incentive engine service"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()
    
    async def test_health_check(self) -> Dict:
        """Test the health check endpoint"""
        print("🏥 Testing health check...")
        try:
            response = await self.client.get(f"{self.base_url}/incentive/health")
            result = response.json()
            print(f"✅ Health check: {result['status']}")
            return result
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_start_tracking(self, user_address: str) -> Dict:
        """Test starting emotion tracking"""
        print(f"🚀 Testing start tracking for {user_address}...")
        try:
            response = await self.client.post(
                f"{self.base_url}/incentive/start-tracking",
                params={"user_address": user_address}
            )
            result = response.json()
            print(f"✅ Started tracking: Session ID {result.get('session_id')}")
            return result
        except Exception as e:
            print(f"❌ Start tracking failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_record_emotion(self, user_address: str, emotion: str, duration: int) -> Dict:
        """Test recording an emotion"""
        print(f"😊 Testing record emotion: {emotion} for {duration}ms...")
        try:
            response = await self.client.post(
                f"{self.base_url}/incentive/record-emotion",
                params={"user_address": user_address},
                json={
                    "emotion": emotion,
                    "duration": duration,
                    "timestamp": int(time.time() * 1000),
                    "confidence": 0.85
                }
            )
            result = response.json()
            print(f"✅ Recorded emotion: {emotion}")
            return result
        except Exception as e:
            print(f"❌ Record emotion failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_end_tracking(self, user_address: str) -> Dict:
        """Test ending emotion tracking"""
        print("🏁 Testing end tracking...")
        try:
            response = await self.client.post(
                f"{self.base_url}/incentive/end-tracking",
                params={"user_address": user_address}
            )
            result = response.json()
            print(f"✅ Ended tracking: {result.get('emotions_recorded')} emotions recorded")
            if 'pending_reward_tokens' in result:
                print(f"💰 Pending reward: {result['pending_reward_tokens']} tokens")
            return result
        except Exception as e:
            print(f"❌ End tracking failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_user_stats(self, user_address: str) -> Dict:
        """Test getting user statistics"""
        print(f"📊 Testing user stats for {user_address}...")
        try:
            response = await self.client.get(
                f"{self.base_url}/incentive/user-stats/{user_address}"
            )
            result = response.json()
            print(f"✅ User stats: {result.get('total_sessions', 0)} sessions")
            return result
        except Exception as e:
            print(f"❌ User stats failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_batch_processing(self, user_address: str) -> Dict:
        """Test batch emotion processing"""
        print("📦 Testing batch emotion processing...")
        
        emotions_data = [
            {"emotion": "happy", "duration": 3000, "timestamp": int(time.time() * 1000)},
            {"emotion": "surprised", "duration": 2000, "timestamp": int(time.time() * 1000) + 1000},
            {"emotion": "neutral", "duration": 4000, "timestamp": int(time.time() * 1000) + 2000},
            {"emotion": "sad", "duration": 1500, "timestamp": int(time.time() * 1000) + 3000},
        ]
        
        try:
            response = await self.client.post(
                f"{self.base_url}/incentive/process-batch",
                json={
                    "user_address": user_address,
                    "emotions": emotions_data
                }
            )
            result = response.json()
            print(f"✅ Batch processed: {result.get('emotions_processed')} emotions")
            if 'pending_reward_tokens' in result:
                print(f"💰 Batch reward: {result['pending_reward_tokens']} tokens")
            return result
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def run_full_test_suite(self) -> Dict:
        """Run the complete test suite"""
        print("🧪 Starting EmoHunter Incentive Engine Test Suite")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Health check
        results['health'] = await self.test_health_check()
        
        # Test 2: Individual session workflow
        print("\n📋 Testing Individual Session Workflow...")
        results['start_tracking'] = await self.test_start_tracking(TEST_USER_ADDRESS)
        
        if results['start_tracking'].get('status') != 'failed':
            # Record multiple emotions
            emotions_to_test = [
                ("happy", 5000),
                ("surprised", 3000),
                ("neutral", 2000),
                ("angry", 1000)
            ]
            
            for emotion, duration in emotions_to_test:
                await self.test_record_emotion(TEST_USER_ADDRESS, emotion, duration)
                await asyncio.sleep(0.5)  # Small delay between emotions
            
            results['end_tracking'] = await self.test_end_tracking(TEST_USER_ADDRESS)
        
        # Test 3: User statistics
        results['user_stats'] = await self.test_user_stats(TEST_USER_ADDRESS)
        
        # Test 4: Batch processing
        print("\n📦 Testing Batch Processing...")
        results['batch_processing'] = await self.test_batch_processing(TEST_USER_ADDRESS + "1")  # Different user
        
        # Test 5: API Documentation
        print("\n📚 Testing API Documentation...")
        try:
            response = await self.client.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible at /docs")
                results['docs'] = {"status": "accessible"}
            else:
                print("❌ API documentation not accessible")
                results['docs'] = {"status": "failed"}
        except Exception as e:
            print(f"❌ API docs test failed: {e}")
            results['docs'] = {"status": "failed", "error": str(e)}
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Test Suite Summary")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('status') not in ['failed', None] else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if status == "✅ PASS":
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Incentive engine is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = IncentiveEngineLocalTester()
    
    try:
        results = await tester.run_full_test_suite()
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🚀 EmoHunter Incentive Engine Local Tester")
    print("Make sure the service is running on http://localhost:8001")
    print("Start the service with: python -m uvicorn service:app --port 8001")
    print()
    
    asyncio.run(main())
