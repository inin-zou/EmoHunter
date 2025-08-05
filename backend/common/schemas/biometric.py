"""
🏥 Biometric Data Schemas

Data models for Apple Watch and other biometric device integration.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class BiometricDataType(str, Enum):
    """Types of biometric data"""
    HEART_RATE = "heart_rate"
    HRV = "hrv"
    SLEEP = "sleep"
    ACTIVITY = "activity"
    STRESS = "stress"


class SleepStage(str, Enum):
    """Sleep stages"""
    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"


class HeartRateData(BaseModel):
    """Heart rate measurement data"""
    timestamp: datetime
    bpm: int = Field(..., ge=30, le=220, description="Beats per minute")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    context: Optional[str] = None  # "resting", "active", "workout", etc.


class RestingHeartRateData(BaseModel):
    """Resting heart rate baseline data (HKQuantityTypeIdentifier.restingHeartRate)"""
    timestamp: datetime
    resting_bpm: int = Field(..., ge=30, le=120, description="Resting heart rate baseline")
    measurement_period_days: int = Field(default=7, description="Period over which resting HR was calculated")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class HRVData(BaseModel):
    """Heart Rate Variability data"""
    timestamp: datetime
    rmssd: float = Field(..., ge=0.0, description="Root Mean Square of Successive Differences (ms)")
    sdnn: Optional[float] = Field(None, ge=0.0, description="Standard Deviation of NN intervals (ms)")
    pnn50: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage of NN50 intervals")
    stress_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Calculated stress score")


class SleepData(BaseModel):
    """Sleep tracking data"""
    date: datetime  # Sleep date (usually previous night)
    bedtime: datetime
    wake_time: datetime
    total_sleep_minutes: int = Field(..., ge=0)
    deep_sleep_minutes: int = Field(..., ge=0)
    light_sleep_minutes: int = Field(..., ge=0)
    rem_sleep_minutes: int = Field(..., ge=0)
    awake_minutes: int = Field(..., ge=0)
    sleep_efficiency: float = Field(..., ge=0.0, le=1.0, description="Sleep efficiency percentage")
    sleep_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)


class ActivityData(BaseModel):
    """Daily activity data"""
    timestamp: datetime
    steps: int = Field(..., ge=0)
    calories_burned: int = Field(..., ge=0)
    active_minutes: int = Field(..., ge=0)
    distance_meters: Optional[float] = Field(None, ge=0.0)
    floors_climbed: Optional[int] = Field(None, ge=0)


class BiometricDataPoint(BaseModel):
    """Generic biometric data point"""
    user_id: str
    device_id: Optional[str] = None
    data_type: BiometricDataType
    timestamp: datetime
    value: float
    unit: str
    metadata: Optional[Dict[str, Any]] = None


class BiometricUploadRequest(BaseModel):
    """Request for uploading biometric data"""
    user_id: str
    device_id: Optional[str] = "apple_watch"
    heart_rate_data: Optional[List[HeartRateData]] = None
    resting_heart_rate_data: Optional[List[RestingHeartRateData]] = None
    hrv_data: Optional[List[HRVData]] = None
    sleep_data: Optional[List[SleepData]] = None
    activity_data: Optional[List[ActivityData]] = None
    upload_timestamp: datetime = Field(default_factory=datetime.now)


class EmotionalBiometricInsight(BaseModel):
    """Emotional insights derived from biometric data"""
    user_id: str
    timestamp: datetime
    primary_emotion_indicator: str  # "stress", "relaxation", "fatigue", "alertness"
    confidence: float = Field(..., ge=0.0, le=1.0)
    contributing_factors: List[str]  # ["elevated_hr", "low_hrv", "poor_sleep"]
    cbt_dbt_recommendations: List[str]  # CBT/DBT techniques to suggest
    contextual_prompt: str  # Natural language context for conversation engine


class BiometricAnalysisResult(BaseModel):
    """Result of biometric data analysis"""
    user_id: str
    analysis_timestamp: datetime
    data_points_analyzed: int
    time_range_hours: float
    insights: List[EmotionalBiometricInsight]
    overall_wellness_score: float = Field(..., ge=0.0, le=100.0)
    recommendations: List[str]
    next_analysis_suggested: datetime


class BiometricTrigger(BaseModel):
    """Biometric-based emotional trigger"""
    trigger_id: str
    user_id: str
    timestamp: datetime
    trigger_type: str  # "stress_spike", "poor_sleep", "low_activity"
    severity: str  # "low", "medium", "high"
    biometric_values: Dict[str, float]
    suggested_emotion_labels: List[str]
    cbt_patterns: List[str]  # Potential cognitive patterns to address
    dbt_skills: List[str]  # DBT skills to recommend
    intervention_priority: int = Field(..., ge=1, le=5)
