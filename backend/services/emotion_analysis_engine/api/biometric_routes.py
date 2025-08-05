"""
🏥 Biometric Data API Routes

API endpoints for Apple Watch and biometric data integration.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from common.utils.logger import get_service_logger
from common.schemas.biometric import (
    BiometricUploadRequest, BiometricAnalysisResult, EmotionalBiometricInsight,
    BiometricTrigger, HeartRateData, HRVData, SleepData, ActivityData
)
from services.biometric_processor import BiometricEmotionProcessor

logger = get_service_logger("biometric_api")

# Create router
router = APIRouter(prefix="/biometric", tags=["biometric"])

# Initialize biometric processor
biometric_processor = BiometricEmotionProcessor()

# In-memory storage for demo (in production, use proper database)
biometric_data_store = {}
analysis_results_store = {}


@router.post("/upload", response_model=BiometricAnalysisResult)
async def upload_biometric_data(
    data: BiometricUploadRequest,
    background_tasks: BackgroundTasks
):
    """
    Upload biometric data from Apple Watch or other devices
    
    This endpoint accepts heart rate, HRV, sleep, and activity data
    and processes it to generate emotional insights.
    """
    try:
        logger.info(f"📱 Received biometric data upload for user {data.user_id}")
        
        # Store raw data (in production, save to database)
        user_key = f"{data.user_id}_{int(datetime.now().timestamp())}"
        biometric_data_store[user_key] = data
        
        # Process the data to generate insights
        analysis_result = biometric_processor.process_biometric_data(data)
        
        # Store analysis result
        analysis_results_store[data.user_id] = analysis_result
        
        # Check for multi-condition triggers
        multi_condition_triggers = biometric_processor.detect_multi_condition_triggers(data, analysis_result.insights)
        
        # Check for high-priority triggers in background
        background_tasks.add_task(
            check_biometric_triggers, 
            data.user_id, 
            analysis_result.insights,
            multi_condition_triggers
        )
        
        logger.info(f"✅ Processed biometric data for {data.user_id}: {len(analysis_result.insights)} insights generated")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"❌ Error processing biometric upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process biometric data: {str(e)}")


@router.get("/analysis/{user_id}", response_model=BiometricAnalysisResult)
async def get_biometric_analysis(user_id: str):
    """Get the latest biometric analysis for a user"""
    try:
        if user_id not in analysis_results_store:
            raise HTTPException(status_code=404, detail="No biometric analysis found for user")
        
        return analysis_results_store[user_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving biometric analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")


@router.get("/insights/{user_id}", response_model=List[EmotionalBiometricInsight])
async def get_emotional_insights(user_id: str, limit: int = 10):
    """Get emotional insights derived from biometric data"""
    try:
        if user_id not in analysis_results_store:
            return []
        
        analysis = analysis_results_store[user_id]
        return analysis.insights[-limit:] if limit else analysis.insights
        
    except Exception as e:
        logger.error(f"❌ Error retrieving emotional insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve insights")


@router.get("/context/{user_id}")
async def get_biometric_context(user_id: str):
    """Get biometric context for conversation engine"""
    try:
        if user_id not in analysis_results_store:
            return {
                "context": "No biometric data available for this user.",
                "insights_count": 0,
                "wellness_score": 75.0
            }
        
        analysis = analysis_results_store[user_id]
        context_prompt = biometric_processor.generate_contextual_prompt(analysis.insights)
        
        return {
            "context": context_prompt,
            "insights_count": len(analysis.insights),
            "wellness_score": analysis.overall_wellness_score,
            "recommendations": analysis.recommendations,
            "last_analysis": analysis.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating biometric context: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate context")


@router.post("/mock/{user_id}")
async def generate_mock_biometric_data(user_id: str):
    """Generate and process mock biometric data when no real data is available"""
    try:
        # Generate mock data
        mock_data = biometric_processor.generate_mock_biometric_data(user_id)
        
        # Process the mock data
        analysis_result = biometric_processor.process_biometric_data(mock_data)
        analysis_results_store[user_id] = analysis_result
        
        logger.info(f"📱 Generated and processed mock biometric data for {user_id}")
        
        return {
            "message": "Mock biometric data generated and processed successfully",
            "user_id": user_id,
            "data_type": "mock_apple_watch_data",
            "data_points": {
                "heart_rate": len(mock_data.heart_rate_data),
                "hrv": len(mock_data.hrv_data),
                "sleep": len(mock_data.sleep_data),
                "activity": len(mock_data.activity_data),
                "resting_hr": len(mock_data.resting_heart_rate_data)
            },
            "insights_generated": len(analysis_result.insights),
            "wellness_score": analysis_result.overall_wellness_score,
            "analysis_result": analysis_result
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating mock biometric data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate mock data: {str(e)}")


@router.post("/simulate")
async def simulate_apple_watch_data(user_id: str = "demo_user"):
    """
    Simulate Apple Watch data for testing purposes
    
    Generates realistic biometric data for development and testing.
    """
    try:
        import random
        from datetime import timedelta
        
        now = datetime.now()
        
        # Simulate heart rate data (last 24 hours)
        heart_rate_data = []
        for i in range(24):
            timestamp = now - timedelta(hours=i)
            # Simulate realistic heart rate with some variation
            base_hr = 70 + random.randint(-10, 20)
            if 9 <= timestamp.hour <= 17:  # Daytime - slightly elevated
                base_hr += random.randint(5, 15)
            
            heart_rate_data.append(HeartRateData(
                timestamp=timestamp,
                bpm=base_hr,
                confidence=random.uniform(0.8, 0.95),
                context="resting" if timestamp.hour < 7 or timestamp.hour > 22 else "active"
            ))
        
        # Simulate HRV data
        hrv_data = []
        for i in range(6):  # Every 4 hours
            timestamp = now - timedelta(hours=i*4)
            rmssd = random.uniform(15, 45)  # Some will be low (stress indicator)
            stress_score = max(0, min(100, 100 - (rmssd * 2)))  # Inverse relationship
            
            hrv_data.append(HRVData(
                timestamp=timestamp,
                rmssd=rmssd,
                sdnn=random.uniform(20, 60),
                pnn50=random.uniform(5, 25),
                stress_score=stress_score
            ))
        
        # Simulate sleep data (last night)
        sleep_start = now.replace(hour=23, minute=0, second=0) - timedelta(days=1)
        sleep_end = now.replace(hour=7, minute=0, second=0)
        total_sleep = 7 * 60  # 7 hours in minutes
        
        sleep_data = [SleepData(
            date=sleep_start.date(),
            bedtime=sleep_start,
            wake_time=sleep_end,
            total_sleep_minutes=total_sleep,
            deep_sleep_minutes=random.randint(60, 120),  # Some may be low
            light_sleep_minutes=random.randint(200, 300),
            rem_sleep_minutes=random.randint(80, 140),
            awake_minutes=random.randint(20, 80),  # Some may be high (stress)
            sleep_efficiency=random.uniform(0.75, 0.95),
            sleep_quality_score=random.uniform(60, 90)
        )]
        
        # Simulate activity data (today)
        activity_data = [ActivityData(
            timestamp=now,
            steps=random.randint(2000, 12000),  # Some may be low (depression indicator)
            calories_burned=random.randint(1500, 2500),
            active_minutes=random.randint(5, 60),  # Some may be very low
            distance_meters=random.uniform(1000, 8000),
            floors_climbed=random.randint(0, 15)
        )]
        
        # Create upload request
        upload_request = BiometricUploadRequest(
            user_id=user_id,
            device_id="simulated_apple_watch",
            heart_rate_data=heart_rate_data,
            hrv_data=hrv_data,
            sleep_data=sleep_data,
            activity_data=activity_data
        )
        
        # Process the simulated data
        analysis_result = biometric_processor.process_biometric_data(upload_request)
        analysis_results_store[user_id] = analysis_result
        
        logger.info(f"🧪 Generated simulated Apple Watch data for {user_id}")
        
        return {
            "message": "Simulated Apple Watch data generated and processed",
            "user_id": user_id,
            "data_points": {
                "heart_rate": len(heart_rate_data),
                "hrv": len(hrv_data),
                "sleep": len(sleep_data),
                "activity": len(activity_data)
            },
            "insights_generated": len(analysis_result.insights),
            "wellness_score": analysis_result.overall_wellness_score,
            "analysis_result": analysis_result
        }
        
    except Exception as e:
        logger.error(f"❌ Error simulating Apple Watch data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate data: {str(e)}")


@router.get("/triggers/{user_id}", response_model=List[BiometricTrigger])
async def get_biometric_triggers(user_id: str):
    """Get biometric triggers that warrant attention"""
    try:
        if user_id not in analysis_results_store:
            return []
        
        analysis = analysis_results_store[user_id]
        triggers = biometric_processor.detect_triggers(analysis.insights)
        
        return triggers
        
    except Exception as e:
        logger.error(f"❌ Error retrieving biometric triggers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve triggers")


@router.get("/health")
async def biometric_health_check():
    """Health check for biometric service"""
    return {
        "status": "healthy",
        "service": "biometric_processor",
        "timestamp": datetime.now().isoformat(),
        "active_users": len(analysis_results_store),
        "processor_status": "active"
    }


async def check_biometric_triggers(
    user_id: str, 
    insights: List[EmotionalBiometricInsight],
    multi_condition_triggers: List[BiometricTrigger] = None
):
    """Background task to check for high-priority biometric triggers"""
    try:
        high_priority_insights = [i for i in insights if i.confidence > 0.85]
        
        if high_priority_insights:
            logger.warning(f"🚨 High-priority biometric triggers detected for user {user_id}")
            # In production, this could trigger notifications, alerts, or immediate interventions
            
        for insight in high_priority_insights:
            logger.info(f"🎯 Trigger: {insight.primary_emotion_indicator} (confidence: {insight.confidence:.1%})")
        
        # Check multi-condition triggers for proactive intervention
        if multi_condition_triggers:
            for trigger in multi_condition_triggers:
                logger.warning(f"🚨 Multi-condition trigger: {trigger.trigger_type} (severity: {trigger.severity})")
                
                # Generate proactive intervention prompt
                intervention_prompt = biometric_processor.generate_proactive_intervention_prompt(trigger)
                logger.info(f"💬 Suggested intervention: {intervention_prompt}")
                
                # In production, this could:
                # 1. Send push notification
                # 2. Initiate proactive conversation
                # 3. Alert healthcare providers
                # 4. Trigger emergency protocols
            
    except Exception as e:
        logger.error(f"❌ Error checking biometric triggers: {e}")


# Additional utility endpoints

@router.delete("/data/{user_id}")
async def clear_user_biometric_data(user_id: str):
    """Clear all biometric data for a user (for testing/privacy)"""
    try:
        # Remove from analysis results
        if user_id in analysis_results_store:
            del analysis_results_store[user_id]
        
        # Remove raw data entries
        keys_to_remove = [k for k in biometric_data_store.keys() if k.startswith(user_id)]
        for key in keys_to_remove:
            del biometric_data_store[key]
        
        logger.info(f"🗑️ Cleared biometric data for user {user_id}")
        
        return {"message": f"Biometric data cleared for user {user_id}"}
        
    except Exception as e:
        logger.error(f"❌ Error clearing biometric data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear data")


@router.get("/stats")
async def get_biometric_stats():
    """Get overall biometric processing statistics"""
    try:
        total_users = len(analysis_results_store)
        total_insights = sum(len(result.insights) for result in analysis_results_store.values())
        
        avg_wellness_score = 0
        if analysis_results_store:
            avg_wellness_score = sum(result.overall_wellness_score for result in analysis_results_store.values()) / total_users
        
        return {
            "total_users": total_users,
            "total_insights_generated": total_insights,
            "average_wellness_score": round(avg_wellness_score, 1),
            "active_analyses": total_users,
            "service_uptime": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving biometric stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")
