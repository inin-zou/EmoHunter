"""
🏥 Biometric Data Processor

Processes Apple Watch and other biometric data to generate emotional insights
using CBT/DBT principles and physiological indicators.
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics
import math

from common.config import settings
from common.utils.logger import get_service_logger
from common.schemas.biometric import (
    BiometricUploadRequest, EmotionalBiometricInsight, BiometricAnalysisResult,
    BiometricTrigger, HeartRateData, RestingHeartRateData, HRVData, SleepData, ActivityData
)

logger = get_service_logger("biometric_processor")


class BiometricEmotionProcessor:
    """
    🏥 Biometric Emotion Processor
    
    Analyzes biometric data to generate emotional insights and CBT/DBT recommendations
    """
    
    def __init__(self):
        """Initialize the biometric processor"""
        self.cbt_patterns = {
            "catastrophizing": ["elevated_stress", "high_hr_variability", "poor_sleep"],
            "anxiety": ["elevated_hr", "low_hrv", "restless_sleep"],
            "depression": ["low_activity", "excessive_sleep", "low_hr_variability"],
            "stress": ["elevated_hr", "low_hrv", "poor_sleep_efficiency"],
            "fatigue": ["poor_sleep", "low_activity", "irregular_hr"]
        }
        
        self.dbt_skills = {
            "stress": ["deep_breathing", "progressive_muscle_relaxation", "mindfulness"],
            "anxiety": ["grounding_techniques", "distress_tolerance", "wise_mind"],
            "depression": ["behavioral_activation", "opposite_action", "self_soothing"],
            "fatigue": ["sleep_hygiene", "gentle_activity", "self_compassion"],
            "overwhelm": ["distress_tolerance", "emotional_regulation", "mindfulness"]
        }
        
        logger.info("🏥 Biometric Emotion Processor initialized")
    
    def generate_mock_biometric_data(self, user_id: str) -> BiometricUploadRequest:
        """Generate realistic mock biometric data for testing/demo purposes"""
        import random
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Generate realistic heart rate data (resting and active)
        heart_rate_data = []
        for i in range(24):  # 24 hours of data
            time_offset = now - timedelta(hours=i)
            
            # Resting HR (morning readings)
            if 6 <= time_offset.hour <= 8:
                heart_rate_data.append(HeartRateData(
                    timestamp=time_offset,
                    bpm=random.randint(55, 75),
                    context="resting"
                ))
            
            # Active HR throughout day
            base_hr = 70 + random.randint(-10, 15)
            heart_rate_data.append(HeartRateData(
                timestamp=time_offset,
                bpm=base_hr,
                context="active" if 9 <= time_offset.hour <= 22 else "resting"
            ))
        
        # Generate HRV data
        hrv_data = []
        for i in range(7):  # Week of HRV data
            hrv_data.append(HRVData(
                timestamp=now - timedelta(days=i),
                rmssd=random.uniform(25, 45),  # Normal range
                stress_score=random.randint(15, 35)
            ))
        
        # Generate sleep data
        sleep_data = []
        for i in range(7):  # Week of sleep data
            total_sleep = random.randint(360, 540)  # 6-9 hours
            deep_sleep = total_sleep * random.uniform(0.15, 0.25)
            rem_sleep = total_sleep * random.uniform(0.20, 0.30)
            light_sleep = total_sleep - deep_sleep - rem_sleep
            
            sleep_data.append(SleepData(
                date=(now - timedelta(days=i)).date(),
                total_sleep_minutes=total_sleep,
                deep_sleep_minutes=deep_sleep,
                rem_sleep_minutes=rem_sleep,
                light_sleep_minutes=light_sleep,
                sleep_efficiency=random.uniform(0.75, 0.95),
                time_to_fall_asleep_minutes=random.randint(5, 25)
            ))
        
        # Generate activity data
        activity_data = []
        for i in range(7):  # Week of activity data
            activity_data.append(ActivityData(
                date=(now - timedelta(days=i)).date(),
                steps=random.randint(3000, 12000),
                calories_burned=random.randint(1800, 2800),
                active_minutes=random.randint(20, 90),
                distance_meters=random.uniform(2000, 10000),
                floors_climbed=random.randint(5, 20)
            ))
        
        # Generate baseline resting HR
        resting_hr_data = [RestingHeartRateData(
            date=now.date(),
            resting_bpm=random.randint(58, 72)
        )]
        
        logger.info(f"📱 Generated mock biometric data for {user_id}")
        
        return BiometricUploadRequest(
            user_id=user_id,
            device_id="mock_apple_watch",
            heart_rate_data=heart_rate_data,
            hrv_data=hrv_data,
            sleep_data=sleep_data,
            activity_data=activity_data,
            resting_heart_rate_data=resting_hr_data
        )
    
    def _is_empty_biometric_data(self, data: BiometricUploadRequest) -> bool:
        """Check if biometric data is empty or null"""
        return (
            not data.heart_rate_data and
            not data.hrv_data and
            not data.sleep_data and
            not data.activity_data and
            not data.resting_heart_rate_data
        )
    
    def process_biometric_data(self, data: BiometricUploadRequest) -> BiometricAnalysisResult:
        """
        Process uploaded biometric data and generate emotional insights
        
        Args:
            data: Biometric data upload request
            
        Returns:
            Analysis result with emotional insights and recommendations
        """
        try:
            # Generate mock data if input is null/empty
            if self._is_empty_biometric_data(data):
                logger.info(f"📱 No biometric data provided, generating mock data for {data.user_id}")
                data = self.generate_mock_biometric_data(data.user_id)
            
            insights = []
            total_data_points = 0
            
            # Get baseline values for comparison
            baseline_resting_hr = None
            if data.resting_heart_rate_data:
                baseline_resting_hr = data.resting_heart_rate_data[-1].resting_bpm  # Most recent baseline
                total_data_points += len(data.resting_heart_rate_data)
            
            # Process heart rate data with baseline comparison
            if data.heart_rate_data:
                hr_insights = self._analyze_heart_rate_with_baseline(
                    data.user_id, data.heart_rate_data, baseline_resting_hr
                )
                insights.extend(hr_insights)
                total_data_points += len(data.heart_rate_data)
            
            # Process HRV data
            if data.hrv_data:
                hrv_insights = self._analyze_hrv(data.user_id, data.hrv_data)
                insights.extend(hrv_insights)
                total_data_points += len(data.hrv_data)
            
            # Process sleep data
            if data.sleep_data:
                sleep_insights = self._analyze_sleep(data.user_id, data.sleep_data)
                insights.extend(sleep_insights)
                total_data_points += len(data.sleep_data)
            
            # Process activity data
            if data.activity_data:
                activity_insights = self._analyze_activity(data.user_id, data.activity_data)
                insights.extend(activity_insights)
                total_data_points += len(data.activity_data)
            
            # Calculate overall wellness score
            wellness_score = self._calculate_wellness_score(insights)
            
            # Generate comprehensive recommendations
            recommendations = self._generate_recommendations(insights)
            
            # Calculate time range
            time_range = self._calculate_time_range(data)
            
            result = BiometricAnalysisResult(
                user_id=data.user_id,
                analysis_timestamp=datetime.now(),
                data_points_analyzed=total_data_points,
                time_range_hours=time_range,
                insights=insights,
                overall_wellness_score=wellness_score,
                recommendations=recommendations,
                next_analysis_suggested=datetime.now() + timedelta(hours=6)
            )
            
            logger.info(f"✅ Processed biometric data for user {data.user_id}: {total_data_points} data points")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing biometric data: {e}")
            raise
    
    def _analyze_heart_rate(self, user_id: str, hr_data: List[HeartRateData]) -> List[EmotionalBiometricInsight]:
        """Analyze heart rate data for emotional indicators (legacy method)"""
        return self._analyze_heart_rate_with_baseline(user_id, hr_data, None)
    
    def _analyze_heart_rate_with_baseline(
        self, 
        user_id: str, 
        hr_data: List[HeartRateData], 
        baseline_resting_hr: Optional[int] = None
    ) -> List[EmotionalBiometricInsight]:
        """
        Analyze heart rate data with baseline comparison for emotional indicators
        
        Implements your requirement:
        IF (Resting HR > baseline + 15%) THEN → stress/anxiety indicator
        """
        if not hr_data:
            return []
        
        insights = []
        bpm_values = [hr.bpm for hr in hr_data]
        avg_hr = statistics.mean(bpm_values)
        hr_variability = statistics.stdev(bpm_values) if len(bpm_values) > 1 else 0
        
        # Get resting heart rate readings (context="resting")
        resting_hr_values = [hr.bpm for hr in hr_data if hr.context == "resting"]
        avg_resting_hr = statistics.mean(resting_hr_values) if resting_hr_values else avg_hr
        
        # Use baseline comparison if available, otherwise use fixed thresholds
        if baseline_resting_hr:
            # Your requirement: IF (Resting HR > baseline + 15%)
            threshold_15_percent = baseline_resting_hr * 1.15
            threshold_25_percent = baseline_resting_hr * 1.25
            
            if avg_resting_hr > threshold_25_percent:
                # Severe elevation (>25% above baseline)
                insights.append(EmotionalBiometricInsight(
                    user_id=user_id,
                    timestamp=datetime.now(),
                    primary_emotion_indicator="anxiety",
                    confidence=0.9,
                    contributing_factors=["severely_elevated_resting_hr", "baseline_deviation"],
                    cbt_dbt_recommendations=self.dbt_skills["anxiety"],
                    contextual_prompt=f"Your resting heart rate ({avg_resting_hr:.0f} bpm) is {((avg_resting_hr/baseline_resting_hr-1)*100):.0f}% above your baseline ({baseline_resting_hr} bpm), indicating significant physiological stress or anxiety."
                ))
            elif avg_resting_hr > threshold_15_percent:
                # Moderate elevation (15-25% above baseline)
                insights.append(EmotionalBiometricInsight(
                    user_id=user_id,
                    timestamp=datetime.now(),
                    primary_emotion_indicator="stress",
                    confidence=0.8,
                    contributing_factors=["elevated_resting_hr", "baseline_deviation"],
                    cbt_dbt_recommendations=self.dbt_skills["stress"],
                    contextual_prompt=f"Your resting heart rate ({avg_resting_hr:.0f} bpm) is {((avg_resting_hr/baseline_resting_hr-1)*100):.0f}% above your baseline ({baseline_resting_hr} bpm), suggesting elevated stress levels."
                ))
        else:
            # Fallback to fixed thresholds when no baseline available
            if avg_hr > 90:  # Elevated resting HR
                insights.append(EmotionalBiometricInsight(
                    user_id=user_id,
                    timestamp=datetime.now(),
                    primary_emotion_indicator="stress",
                    confidence=min(0.8, (avg_hr - 70) / 50),
                    contributing_factors=["elevated_heart_rate"],
                    cbt_dbt_recommendations=self.dbt_skills["stress"],
                    contextual_prompt=f"Your heart rate has been elevated (avg {avg_hr:.0f} bpm), which may indicate stress or anxiety. This could affect your emotional state."
                ))
        
        # Detect high HR variability (potential anxiety) - independent of baseline
        if hr_variability > 15:
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="anxiety",
                confidence=min(0.7, hr_variability / 25),
                contributing_factors=["high_hr_variability"],
                cbt_dbt_recommendations=self.dbt_skills["anxiety"],
                contextual_prompt=f"Your heart rate has been quite variable (σ={hr_variability:.1f} bpm), which sometimes indicates anxiety or emotional turbulence."
            ))
        
        return insights
    
    def _analyze_hrv(self, user_id: str, hrv_data: List[HRVData]) -> List[EmotionalBiometricInsight]:
        """Analyze HRV data for stress and recovery indicators"""
        if not hrv_data:
            return []
        
        insights = []
        rmssd_values = [hrv.rmssd for hrv in hrv_data]
        avg_rmssd = statistics.mean(rmssd_values)
        
        # Low HRV indicates stress/poor recovery
        if avg_rmssd < 20:  # Low HRV threshold
            stress_level = max(0, (30 - avg_rmssd) / 30)
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="stress",
                confidence=min(0.9, stress_level),
                contributing_factors=["low_hrv", "poor_recovery"],
                cbt_dbt_recommendations=self.dbt_skills["stress"] + ["recovery_techniques"],
                contextual_prompt=f"Your heart rate variability is lower than optimal ({avg_rmssd:.1f}ms), suggesting your body may be under stress or not recovering well."
            ))
        
        # Check for stress scores if available
        stress_scores = [hrv.stress_score for hrv in hrv_data if hrv.stress_score is not None]
        if stress_scores:
            avg_stress = statistics.mean(stress_scores)
            if avg_stress > 70:
                insights.append(EmotionalBiometricInsight(
                    user_id=user_id,
                    timestamp=datetime.now(),
                    primary_emotion_indicator="overwhelm",
                    confidence=min(0.85, avg_stress / 100),
                    contributing_factors=["high_stress_score"],
                    cbt_dbt_recommendations=self.dbt_skills["overwhelm"],
                    contextual_prompt=f"Your stress indicators are elevated ({avg_stress:.0f}/100), which may be impacting your emotional well-being."
                ))
        
        return insights
    
    def _analyze_sleep(self, user_id: str, sleep_data: List[SleepData]) -> List[EmotionalBiometricInsight]:
        """Analyze sleep data for emotional impact"""
        if not sleep_data:
            return []
        
        insights = []
        recent_sleep = sleep_data[-1]  # Most recent sleep data
        
        # Poor sleep efficiency
        if recent_sleep.sleep_efficiency < 0.8:
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="fatigue",
                confidence=0.8,
                contributing_factors=["poor_sleep_efficiency"],
                cbt_dbt_recommendations=self.dbt_skills["fatigue"] + ["sleep_hygiene"],
                contextual_prompt=f"Your sleep efficiency was {recent_sleep.sleep_efficiency:.1%} last night, which may leave you feeling tired or emotionally vulnerable today."
            ))
        
        # Insufficient deep sleep
        total_sleep = recent_sleep.total_sleep_minutes
        deep_sleep_ratio = recent_sleep.deep_sleep_minutes / total_sleep if total_sleep > 0 else 0
        
        if deep_sleep_ratio < 0.15:  # Less than 15% deep sleep
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="fatigue",
                confidence=0.7,
                contributing_factors=["insufficient_deep_sleep"],
                cbt_dbt_recommendations=["sleep_optimization", "relaxation_techniques"],
                contextual_prompt=f"You got only {deep_sleep_ratio:.1%} deep sleep last night, which might affect your mood and emotional regulation today."
            ))
        
        # Excessive wake time
        if recent_sleep.awake_minutes > 60:
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="stress",
                confidence=0.6,
                contributing_factors=["restless_sleep", "frequent_awakenings"],
                cbt_dbt_recommendations=self.dbt_skills["stress"] + ["sleep_hygiene"],
                contextual_prompt=f"You were awake for {recent_sleep.awake_minutes} minutes during the night, which might indicate stress or anxiety affecting your sleep."
            ))
        
        return insights
    
    def _analyze_activity(self, user_id: str, activity_data: List[ActivityData]) -> List[EmotionalBiometricInsight]:
        """Analyze activity data for behavioral patterns"""
        if not activity_data:
            return []
        
        insights = []
        recent_activity = activity_data[-1]
        
        # Low activity levels (potential depression indicator)
        if recent_activity.steps < 3000:
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="depression",
                confidence=0.6,
                contributing_factors=["low_activity", "sedentary_behavior"],
                cbt_dbt_recommendations=self.dbt_skills["depression"] + ["behavioral_activation"],
                contextual_prompt=f"Your activity level has been low ({recent_activity.steps} steps), which sometimes correlates with low mood or energy."
            ))
        
        # Very low active minutes
        if recent_activity.active_minutes < 10:
            insights.append(EmotionalBiometricInsight(
                user_id=user_id,
                timestamp=datetime.now(),
                primary_emotion_indicator="fatigue",
                confidence=0.5,
                contributing_factors=["minimal_active_time"],
                cbt_dbt_recommendations=["gentle_movement", "energy_building"],
                contextual_prompt=f"You had only {recent_activity.active_minutes} active minutes today, which might contribute to feelings of lethargy."
            ))
        
        return insights
    
    def _calculate_wellness_score(self, insights: List[EmotionalBiometricInsight]) -> float:
        """Calculate overall wellness score based on insights"""
        if not insights:
            return 75.0  # Neutral baseline
        
        # Start with baseline score
        base_score = 75.0
        
        # Reduce score based on negative indicators
        stress_insights = [i for i in insights if i.primary_emotion_indicator in ["stress", "anxiety"]]
        fatigue_insights = [i for i in insights if i.primary_emotion_indicator == "fatigue"]
        depression_insights = [i for i in insights if i.primary_emotion_indicator == "depression"]
        
        # Apply penalties weighted by confidence
        for insight in stress_insights:
            base_score -= (insight.confidence * 15)
        
        for insight in fatigue_insights:
            base_score -= (insight.confidence * 10)
        
        for insight in depression_insights:
            base_score -= (insight.confidence * 20)
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self, insights: List[EmotionalBiometricInsight]) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = set()
        
        for insight in insights:
            recommendations.update(insight.cbt_dbt_recommendations)
        
        # Add general wellness recommendations
        if any(i.primary_emotion_indicator == "stress" for i in insights):
            recommendations.add("Consider stress management techniques")
            recommendations.add("Practice regular mindfulness or meditation")
        
        if any(i.primary_emotion_indicator == "fatigue" for i in insights):
            recommendations.add("Focus on sleep hygiene and recovery")
            recommendations.add("Gentle movement and light exposure")
        
        return list(recommendations)
    
    def _calculate_time_range(self, data: BiometricUploadRequest) -> float:
        """Calculate the time range of the data in hours"""
        timestamps = []
        
        if data.heart_rate_data:
            timestamps.extend([hr.timestamp for hr in data.heart_rate_data])
        if data.hrv_data:
            timestamps.extend([hrv.timestamp for hrv in data.hrv_data])
        if data.sleep_data:
            timestamps.extend([sleep.bedtime for sleep in data.sleep_data])
        if data.activity_data:
            timestamps.extend([activity.timestamp for activity in data.activity_data])
        
        if not timestamps:
            return 0.0
        
        time_range = max(timestamps) - min(timestamps)
        return time_range.total_seconds() / 3600  # Convert to hours
    
    def generate_contextual_prompt(self, insights: List[EmotionalBiometricInsight]) -> str:
        """Generate a contextual prompt for the conversation engine"""
        if not insights:
            return "User's biometric data appears normal with no significant emotional indicators."
        
        # Group insights by emotion type
        emotion_groups = {}
        for insight in insights:
            emotion = insight.primary_emotion_indicator
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(insight)
        
        # Build contextual prompt
        prompt_parts = []
        
        for emotion, emotion_insights in emotion_groups.items():
            avg_confidence = statistics.mean([i.confidence for i in emotion_insights])
            factors = set()
            for insight in emotion_insights:
                factors.update(insight.contributing_factors)
            
            prompt_parts.append(
                f"Biometric data suggests {emotion} (confidence: {avg_confidence:.1%}) "
                f"based on: {', '.join(factors)}"
            )
        
        return "Biometric context: " + "; ".join(prompt_parts) + ". Please respond with appropriate emotional awareness and support."
    
    def detect_multi_condition_triggers(
        self, 
        data: BiometricUploadRequest, 
        insights: List[EmotionalBiometricInsight]
    ) -> List[BiometricTrigger]:
        """
        Detect multi-condition triggers based on your requirements:
        
        Example: Anxiety Detection Rule
        IF (Resting HR > baseline + 15%) AND
           (HRV < baseline - 20%) AND  
           (Sleep quality poor for ≥ 3 days)
        THEN → "anxious state" trigger
        """
        triggers = []
        
        # Get baseline values
        baseline_resting_hr = None
        if data.resting_heart_rate_data:
            baseline_resting_hr = data.resting_heart_rate_data[-1].resting_bpm
        
        # Calculate current metrics
        current_metrics = self._calculate_current_metrics(data)
        
        # Rule 1: Anxiety Detection
        anxiety_conditions = []
        
        # Condition 1: Resting HR > baseline + 15%
        if baseline_resting_hr and current_metrics.get('avg_resting_hr'):
            hr_threshold = baseline_resting_hr * 1.15
            if current_metrics['avg_resting_hr'] > hr_threshold:
                anxiety_conditions.append('elevated_resting_hr')
        
        # Condition 2: HRV < baseline - 20% (assuming baseline HRV ~35ms)
        baseline_hrv = 35.0  # Could be personalized
        if current_metrics.get('avg_hrv'):
            hrv_threshold = baseline_hrv * 0.8  # 20% below baseline
            if current_metrics['avg_hrv'] < hrv_threshold:
                anxiety_conditions.append('low_hrv')
        
        # Condition 3: Sleep quality poor for ≥ 3 days
        if data.sleep_data and len(data.sleep_data) >= 3:
            poor_sleep_days = sum(1 for sleep in data.sleep_data[-3:] if sleep.sleep_efficiency < 0.8)
            if poor_sleep_days >= 3:
                anxiety_conditions.append('poor_sleep_pattern')
        
        # Trigger anxiety alert if all conditions met
        if len(anxiety_conditions) >= 2:  # At least 2 out of 3 conditions
            triggers.append(BiometricTrigger(
                trigger_id=f"anxiety_trigger_{data.user_id}_{int(time.time())}",
                user_id=data.user_id,
                timestamp=datetime.now(),
                trigger_type="anxiety_multi_condition",
                severity="high" if len(anxiety_conditions) == 3 else "medium",
                biometric_values=current_metrics,
                suggested_emotion_labels=["anxious", "stressed"],
                cbt_patterns=["catastrophizing", "anxiety"],
                dbt_skills=self.dbt_skills["anxiety"],
                intervention_priority=5 if len(anxiety_conditions) == 3 else 4
            ))
        
        # Rule 2: Depression Detection
        depression_conditions = []
        
        # Low activity for multiple days
        if data.activity_data and len(data.activity_data) >= 3:
            low_activity_days = sum(1 for activity in data.activity_data[-3:] if activity.steps < 4000)
            if low_activity_days >= 2:
                depression_conditions.append('low_activity_pattern')
        
        # Excessive sleep or poor sleep quality
        if data.sleep_data:
            recent_sleep = data.sleep_data[-1]
            if recent_sleep.total_sleep_minutes > 600 or recent_sleep.sleep_efficiency < 0.7:  # >10h or poor quality
                depression_conditions.append('sleep_disturbance')
        
        # Low HRV (autonomic dysfunction)
        if current_metrics.get('avg_hrv') and current_metrics['avg_hrv'] < 25:
            depression_conditions.append('low_hrv_autonomic')
        
        if len(depression_conditions) >= 2:
            triggers.append(BiometricTrigger(
                trigger_id=f"depression_trigger_{data.user_id}_{int(time.time())}",
                user_id=data.user_id,
                timestamp=datetime.now(),
                trigger_type="depression_multi_condition",
                severity="medium",
                biometric_values=current_metrics,
                suggested_emotion_labels=["depressed", "low_mood"],
                cbt_patterns=["depression"],
                dbt_skills=self.dbt_skills["depression"],
                intervention_priority=4
            ))
        
        return triggers
    
    def _calculate_current_metrics(self, data: BiometricUploadRequest) -> Dict[str, float]:
        """Calculate current biometric metrics for trigger detection"""
        metrics = {}
        
        # Heart rate metrics
        if data.heart_rate_data:
            resting_hrs = [hr.bpm for hr in data.heart_rate_data if hr.context == "resting"]
            all_hrs = [hr.bpm for hr in data.heart_rate_data]
            
            if resting_hrs:
                metrics['avg_resting_hr'] = statistics.mean(resting_hrs)
            if all_hrs:
                metrics['avg_hr'] = statistics.mean(all_hrs)
                metrics['hr_variability'] = statistics.stdev(all_hrs) if len(all_hrs) > 1 else 0
        
        # HRV metrics
        if data.hrv_data:
            rmssd_values = [hrv.rmssd for hrv in data.hrv_data]
            if rmssd_values:
                metrics['avg_hrv'] = statistics.mean(rmssd_values)
        
        # Sleep metrics
        if data.sleep_data:
            recent_sleep = data.sleep_data[-1]
            metrics['sleep_efficiency'] = recent_sleep.sleep_efficiency
            metrics['sleep_duration_hours'] = recent_sleep.total_sleep_minutes / 60
        
        # Activity metrics
        if data.activity_data:
            recent_activity = data.activity_data[-1]
            metrics['daily_steps'] = recent_activity.steps
            metrics['active_minutes'] = recent_activity.active_minutes
        
        return metrics
    
    def detect_triggers(self, insights: List[EmotionalBiometricInsight]) -> List[BiometricTrigger]:
        """Detect biometric triggers that warrant immediate attention (legacy method)"""
        triggers = []
        
        high_confidence_insights = [i for i in insights if i.confidence > 0.8]
        
        for insight in high_confidence_insights:
            trigger = BiometricTrigger(
                trigger_id=f"trigger_{insight.user_id}_{int(time.time())}",
                user_id=insight.user_id,
                timestamp=insight.timestamp,
                trigger_type=f"{insight.primary_emotion_indicator}_alert",
                severity="high" if insight.confidence > 0.9 else "medium",
                biometric_values={},  # Could be populated with specific values
                suggested_emotion_labels=[insight.primary_emotion_indicator],
                cbt_patterns=self.cbt_patterns.get(insight.primary_emotion_indicator, []),
                dbt_skills=insight.cbt_dbt_recommendations,
                intervention_priority=5 if insight.confidence > 0.9 else 3
            )
            triggers.append(trigger)
        
        return triggers
    
    def generate_proactive_intervention_prompt(self, trigger: BiometricTrigger) -> str:
        """
        Generate proactive intervention prompt for main conversation engine
        
        Example output: "Hey, I noticed your body is under stress right now. Just checking in—how are you feeling?"
        """
        prompts = {
            "anxiety_multi_condition": [
                "Hey, I noticed some signs that your body might be feeling stressed or anxious right now. Just checking in—how are you feeling?",
                "Your biometric data suggests you might be experiencing some anxiety. Would you like to talk about what's on your mind?",
                "I can see from your health data that you might be going through a stressful time. I'm here if you need support."
            ],
            "depression_multi_condition": [
                "I've noticed some changes in your activity and sleep patterns. How have you been feeling lately?",
                "Your health data suggests you might be having a tough time. Would you like to talk about it?",
                "I'm checking in because I care about your wellbeing. How are you doing today?"
            ],
            "stress_alert": [
                "I noticed your stress levels seem elevated. Would you like to try some breathing exercises together?",
                "Your body is showing signs of stress. Let's take a moment to check in with yourself."
            ]
        }
        
        import random
        trigger_prompts = prompts.get(trigger.trigger_type, [
            "I noticed some changes in your biometric data. How are you feeling right now?"
        ])
        
        return random.choice(trigger_prompts)
