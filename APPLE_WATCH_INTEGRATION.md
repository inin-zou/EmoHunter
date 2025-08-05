# 🍎 Apple Watch Integration Guide

## Overview

EmoHunter now supports Apple Watch biometric data integration, enabling comprehensive emotional analysis by combining facial emotion detection with physiological indicators. This integration uses CBT/DBT principles to generate emotional insights from heart rate, HRV, sleep, and activity data.

## 🏥 Supported Biometric Data

### Heart Rate Data
- **Metrics**: BPM, variability, context (resting/active)
- **Emotional Indicators**: 
  - Elevated HR (>85 bpm) → Stress/Anxiety
  - High variability → Emotional turbulence

### Heart Rate Variability (HRV)
- **Metrics**: RMSSD, SDNN, pNN50, stress score
- **Emotional Indicators**:
  - Low HRV (<25ms) → Stress/Poor recovery
  - High stress score (>70) → Overwhelm

### Sleep Data
- **Metrics**: Sleep efficiency, deep sleep %, wake time
- **Emotional Indicators**:
  - Poor efficiency (<80%) → Fatigue
  - Low deep sleep (<15%) → Mood vulnerability
  - Frequent awakenings → Stress/Anxiety

### Activity Data
- **Metrics**: Steps, active minutes, calories
- **Emotional Indicators**:
  - Low activity (<4000 steps) → Depression risk
  - Minimal active time (<10 min) → Lethargy

## 🔗 API Endpoints

### Upload Biometric Data
```http
POST /api/v1/biometric/upload
Content-Type: application/json

{
  "user_id": "user123",
  "device_id": "apple_watch",
  "heart_rate_data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "bpm": 75,
      "confidence": 0.95,
      "context": "resting"
    }
  ],
  "hrv_data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "rmssd": 35.5,
      "stress_score": 25.0
    }
  ],
  "sleep_data": [
    {
      "date": "2024-01-01",
      "bedtime": "2024-01-01T23:00:00Z",
      "wake_time": "2024-01-02T07:00:00Z",
      "total_sleep_minutes": 480,
      "deep_sleep_minutes": 90,
      "sleep_efficiency": 0.85
    }
  ],
  "activity_data": [
    {
      "timestamp": "2024-01-01T23:59:59Z",
      "steps": 8500,
      "active_minutes": 45,
      "calories_burned": 2200
    }
  ]
}
```

### Get Biometric Context
```http
GET /api/v1/biometric/context/{user_id}
```

Response:
```json
{
  "context": "Biometric data suggests stress (confidence: 75%) based on: elevated_heart_rate, low_hrv. Overall wellness score: 65/100.",
  "insights_count": 2,
  "wellness_score": 65.0,
  "recommendations": ["deep_breathing", "stress_management", "mindfulness"],
  "last_analysis": "2024-01-01T12:00:00Z"
}
```

### Simulate Apple Watch Data
```http
POST /api/v1/biometric/simulate
Content-Type: application/json

{
  "user_id": "demo_user"
}
```

### Integrated Emotion Analysis
```http
GET /current_emotion?user_id={user_id}
```

Returns combined facial emotion + biometric context.

## 🧠 CBT/DBT Integration

### Cognitive Pattern Recognition

The system identifies potential cognitive patterns based on biometric indicators:

| Pattern | Biometric Indicators | CBT/DBT Recommendations |
|---------|---------------------|------------------------|
| **Catastrophizing** | Elevated stress, high HR variability, poor sleep | Cognitive restructuring, reality testing |
| **Anxiety** | Elevated HR, low HRV, restless sleep | Grounding techniques, distress tolerance |
| **Depression** | Low activity, excessive sleep, low HR variability | Behavioral activation, opposite action |
| **Stress** | Elevated HR, low HRV, poor sleep efficiency | Progressive muscle relaxation, mindfulness |
| **Fatigue** | Poor sleep, low activity, irregular HR | Sleep hygiene, gentle activity, self-compassion |

### DBT Skills Recommendations

Based on detected emotional patterns:

- **Stress/Overwhelm**: Deep breathing, progressive muscle relaxation, mindfulness
- **Anxiety**: Grounding techniques, distress tolerance, wise mind
- **Depression**: Behavioral activation, opposite action, self-soothing
- **Fatigue**: Sleep hygiene, gentle activity, self-compassion

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_apple_watch_integration.py
```

This will test:
- ✅ Apple Watch data simulation
- ✅ Biometric context generation
- ✅ Integrated emotion analysis
- ✅ Biometric-aware conversation
- ✅ CBT/DBT pattern recognition

## 💡 Implementation Examples

### Basic Integration
```python
import requests

# 1. Simulate Apple Watch data
response = requests.post("http://localhost:8000/api/v1/biometric/simulate", 
                        json={"user_id": "user123"})

# 2. Get integrated emotion analysis
emotion_response = requests.get("http://localhost:8000/current_emotion?user_id=user123")

# 3. Have biometric-aware conversation
conversation = requests.post("http://localhost:8000/generate", json={
    "message": "I'm feeling stressed today",
    "user_id": "user123",
    "session_id": "session_123"
})
```

### Real Apple Watch Integration (iOS)

For real Apple Watch integration, you would:

1. **iOS App**: Use HealthKit to collect biometric data
2. **Data Processing**: Format data according to our schema
3. **API Upload**: Send data to `/api/v1/biometric/upload`
4. **Real-time Updates**: Stream data for continuous monitoring

```swift
// iOS HealthKit example (pseudo-code)
import HealthKit

func uploadBiometricData() {
    let healthStore = HKHealthStore()
    
    // Collect heart rate data
    let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
    
    // Format and upload to EmoHunter API
    let biometricData = [
        "user_id": userId,
        "heart_rate_data": heartRateReadings,
        "hrv_data": hrvReadings,
        // ... other data
    ]
    
    // POST to /api/v1/biometric/upload
}
```

## 🔧 Configuration

### Emotion Thresholds

Customize detection thresholds in your configuration:

```python
# Heart rate thresholds
ELEVATED_HR_THRESHOLD = 85  # bpm
HIGH_HR_VARIABILITY = 15    # bpm

# HRV thresholds  
LOW_HRV_THRESHOLD = 25      # ms RMSSD
HIGH_STRESS_THRESHOLD = 70  # stress score

# Sleep thresholds
POOR_SLEEP_EFFICIENCY = 0.8 # 80%
LOW_DEEP_SLEEP_RATIO = 0.15 # 15%

# Activity thresholds
LOW_STEP_COUNT = 4000       # steps/day
LOW_ACTIVE_MINUTES = 10     # minutes/day
```

### Wellness Score Calculation

The wellness score (0-100) is calculated based on:
- **Baseline**: 75 points
- **Stress indicators**: -15 points per high-confidence stress insight
- **Fatigue indicators**: -10 points per fatigue insight  
- **Depression indicators**: -20 points per depression insight

## 🚀 Next Steps

### Planned Enhancements

1. **Real-time Streaming**: WebSocket support for live biometric monitoring
2. **Advanced Pattern Recognition**: Machine learning for personalized thresholds
3. **Intervention Triggers**: Automatic alerts for concerning patterns
4. **Historical Analysis**: Trend analysis and long-term wellness tracking
5. **Multi-device Support**: Integration with other wearables (Fitbit, Garmin, etc.)

### Integration Roadmap

- [ ] iOS HealthKit integration
- [ ] Android Health Connect support
- [ ] Real-time biometric streaming
- [ ] Personalized threshold learning
- [ ] Advanced CBT/DBT pattern recognition
- [ ] Intervention trigger system
- [ ] Historical trend analysis
- [ ] Multi-device synchronization

## 📚 Resources

- [Apple HealthKit Documentation](https://developer.apple.com/documentation/healthkit)
- [CBT Techniques Reference](https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral)
- [DBT Skills Overview](https://behavioraltech.org/resources/faqs/dialectical-behavior-therapy-dbt/)
- [Heart Rate Variability Research](https://www.frontiersin.org/articles/10.3389/fpsyg.2017.00213/full)

---

**Built with ❤️ for comprehensive emotional wellness**

*This integration represents the future of personalized mental health support, combining cutting-edge biometric analysis with evidence-based therapeutic approaches.*
