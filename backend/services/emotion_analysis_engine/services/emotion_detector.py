"""
🎭 Emotion Detection Service

Core emotion detection functionality using OpenCV and FER library.
"""

import time
import random
import numpy as np
from typing import Dict, List, Optional, Tuple
import cv2

from common.config import settings
from common.utils.logger import get_service_logger
from common.schemas.emotion import EmotionData

logger = get_service_logger("emotion_detector")

# Try to import FER with fallback to mock
try:
    from fer import FER
    FER_AVAILABLE = True
    logger.info("✅ FER library loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ FER library not available: {e}")
    logger.info("🔄 Using mock emotion detection for development")
    FER_AVAILABLE = False


class MockFER:
    """Mock FER class for development when real FER is not available"""
    def __init__(self, mtcnn=True):
        self.emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
        self.last_mock_emotion = "neutral"
    
    def detect_emotions(self, frame):
        # Mock emotion detection with realistic stability behavior
        if hasattr(self, 'last_mock_emotion') and random.random() < 0.7:
            # 70% chance to keep the same emotion for stability
            emotion = self.last_mock_emotion
            confidence = random.uniform(0.75, 0.95)
        else:
            # 30% chance to change to a new emotion
            emotion = random.choice(self.emotions)
            confidence = random.uniform(0.6, 0.85)
            self.last_mock_emotion = emotion
            logger.info(f"🎭 Emotion changed to: {emotion}")
        
        emotions_dict = {e: 0.1 for e in self.emotions}
        emotions_dict[emotion] = confidence
        
        return [{"emotions": emotions_dict}]


class EmotionDetector:
    """
    🎭 Emotion Detection Service
    
    Handles real-time facial emotion detection with stability algorithms
    """
    
    def __init__(self):
        """Initialize the emotion detector"""
        self.current_emotion = "neutral"
        self.last_emotion = "neutral"
        self.emotion_stability_count = 0
        self.emotion_history: List[str] = []
        self.confidence_history: List[float] = []
        self.camera = None
        self.is_streaming = False
        
        # Initialize emotion detector
        if FER_AVAILABLE:
            self.emotion_detector = FER(mtcnn=True)
        else:
            self.emotion_detector = MockFER(mtcnn=True)
        
        # Emotion classes
        self.emotion_classes = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
        
        logger.info("🎭 Emotion Detector initialized")
    
    def start_camera_stream(self, camera_index: int = 0) -> bool:
        """Start camera stream for emotion detection"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                logger.error(f"❌ Failed to open camera {camera_index}")
                return False
            
            self.is_streaming = True
            logger.info(f"📹 Camera stream started on index {camera_index}")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting camera: {e}")
            return False
    
    def stop_camera_stream(self):
        """Stop camera stream"""
        if self.camera:
            self.camera.release()
            self.camera = None
        self.is_streaming = False
        logger.info("📹 Camera stream stopped")
    
    def capture_and_analyze(self) -> Optional[EmotionData]:
        """Capture frame from camera and analyze emotion"""
        if not self.is_streaming or not self.camera:
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.warning("⚠️ Failed to capture frame")
            return None
        
        return self.analyze_frame(frame)
    
    def analyze_frame(self, frame: np.ndarray) -> Optional[EmotionData]:
        """
        Analyze a single frame for emotion detection
        
        Args:
            frame: Input image frame as numpy array
            
        Returns:
            EmotionData containing analysis results
        """
        try:
            # Detect emotions using FER or mock
            result = self.emotion_detector.detect_emotions(frame)
            
            if result and len(result) > 0:
                # Get the dominant emotion
                emotions = result[0]['emotions']
                dominant_emotion = max(emotions, key=emotions.get)
                confidence = emotions[dominant_emotion]
                
                # Apply stability logic
                stable_emotion, is_stable = self._apply_stability_logic(dominant_emotion, confidence)
                
                # Update emotion history
                self._update_history(dominant_emotion, confidence)
                
                # Get face coordinates if available
                face_coords = None
                if 'box' in result[0]:
                    box = result[0]['box']
                    face_coords = {
                        'x': box[0],
                        'y': box[1],
                        'width': box[2],
                        'height': box[3]
                    }
                
                return EmotionData(
                    emotion=stable_emotion,
                    confidence=confidence,
                    face_coordinates=face_coords
                )
            else:
                logger.warning("⚠️ No face detected in frame")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error analyzing frame: {e}")
            return None
    
    def _apply_stability_logic(self, detected_emotion: str, confidence: float) -> Tuple[str, bool]:
        """
        Apply stability logic to prevent rapid emotion switching
        
        Args:
            detected_emotion: The raw detected emotion
            confidence: Confidence score of the detection
            
        Returns:
            Tuple of (stable_emotion, is_stable_flag)
        """
        # Check if emotion is the same as last detection
        if detected_emotion == self.last_emotion:
            self.emotion_stability_count += 1
        else:
            self.emotion_stability_count = 1
        
        # Determine if we should change the current emotion
        is_stable = False
        
        # Rule 1: Emotion is stable if consistent over threshold frames
        if self.emotion_stability_count >= settings.emotion_stability_threshold:
            self.current_emotion = detected_emotion
            self.last_emotion = detected_emotion
            is_stable = True
        
        # Rule 2: High confidence can override immediately
        elif confidence > settings.emotion_confidence_threshold:
            self.current_emotion = detected_emotion
            self.last_emotion = detected_emotion
            is_stable = True
            logger.info(f"🎯 High confidence emotion change: {detected_emotion} ({confidence:.1%})")
        
        # Rule 3: Medium confidence uses smoothing
        elif 0.6 <= confidence <= settings.emotion_confidence_threshold:
            # Keep current emotion but update last_emotion for tracking
            self.last_emotion = detected_emotion
            is_stable = False
        
        return self.current_emotion, is_stable
    
    def _update_history(self, emotion: str, confidence: float):
        """Update emotion and confidence history for smoothing"""
        self.emotion_history.append(emotion)
        self.confidence_history.append(confidence)
        
        # Keep only configured history size
        if len(self.emotion_history) > settings.emotion_history_size:
            self.emotion_history.pop(0)
            self.confidence_history.pop(0)
    
    def get_current_emotion(self) -> EmotionData:
        """Get current emotion state"""
        # Calculate average confidence from recent history
        recent_confidences = self.confidence_history[-3:] if self.confidence_history else [0.0]
        avg_confidence = sum(recent_confidences) / len(recent_confidences)
        
        return EmotionData(
            emotion=self.current_emotion,
            confidence=avg_confidence
        )
    
    def get_emotion_history(self) -> List[EmotionData]:
        """Get recent emotion history"""
        history = []
        for i, emotion in enumerate(self.emotion_history[-5:]):  # Last 5 emotions
            confidence = self.confidence_history[-(5-i)] if i < len(self.confidence_history) else 0.0
            history.append(EmotionData(emotion=emotion, confidence=confidence))
        return history
    
    def reset_state(self):
        """Reset emotion detection state"""
        self.current_emotion = "neutral"
        self.last_emotion = "neutral"
        self.emotion_stability_count = 0
        self.emotion_history.clear()
        self.confidence_history.clear()
        logger.info("🔄 Emotion detector state reset")
    
    def get_status(self) -> Dict:
        """Get detector status information"""
        return {
            "status": "active" if self.is_streaming else "inactive",
            "current_emotion": self.current_emotion,
            "confidence": sum(self.confidence_history[-3:]) / len(self.confidence_history[-3:]) if self.confidence_history else 0.0,
            "stability_count": self.emotion_stability_count,
            "fer_available": FER_AVAILABLE,
            "camera_active": self.is_streaming,
            "history_size": len(self.emotion_history)
        }
