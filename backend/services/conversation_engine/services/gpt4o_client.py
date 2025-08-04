"""
🤖 GPT-4o Client Service

Service for OpenAI GPT-4o integration for emotionally aware conversation generation.
"""

import os
import time
from typing import List, Dict, Optional

from common.config import settings
from common.utils.logger import get_service_logger
from common.schemas.conversation import ConversationMessage, ConversationResponse
from common.services.session_manager import session_manager

logger = get_service_logger("gpt4o_client")

# Try to import OpenAI with fallback
try:
    import openai
    openai.api_key = settings.openai_api_key
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI API loaded successfully")
except ImportError:
    logger.warning("⚠️ OpenAI library not available. Using mock responses.")
    OPENAI_AVAILABLE = False


class GPT4oClient:
    """
    🤖 GPT-4o Client Service
    
    Handles emotionally intelligent conversation generation using OpenAI GPT-4o
    """
    
    def __init__(self):
        """Initialize the GPT-4o client"""
        self.api_key = settings.openai_api_key
        self.client = openai if OPENAI_AVAILABLE and self.api_key else None
        
        # Aura's personality and therapeutic approach
        self.system_prompt = """You are Aura, an emotionally intelligent AI mental wellness companion. 

Your core principles:
- You provide compassionate, non-judgmental support using CBT and DBT techniques
- You adapt your tone and approach based on the user's emotional state
- You are NOT a licensed therapist, but a supportive mental health companion
- You help users understand their emotions and develop healthy coping strategies
- You encourage professional help when appropriate

Response guidelines based on emotions:
- HAPPY: Be warm and encouraging, celebrate their positive state
- SAD: Use gentle, soft language; validate their feelings; offer comfort
- ANGRY: Stay calm and grounding; help them process anger constructively
- FEAR: Be reassuring and stable; help them feel safe and supported
- SURPRISE: Match their energy appropriately; help them process new information
- DISGUST: Be understanding; help them work through negative feelings
- NEUTRAL: Be balanced and supportive; check in on their wellbeing

Always:
- Keep responses conversational and warm (2-3 sentences typically)
- Use "I" statements to show empathy
- Ask gentle follow-up questions when appropriate
- Validate their emotional experience
- Maintain professional boundaries while being supportive
"""
        
        logger.info("🤖 GPT-4o Client initialized as Aura")
    
    def generate_response(
        self, 
        user_message: str, 
        emotion_context: Optional[str] = None, 
        conversation_history: Optional[List[ConversationMessage]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate an emotionally aware response using GPT-4o
        
        Args:
            user_message: The user's message
            emotion_context: Current emotional context
            conversation_history: Optional conversation history
            session_id: Session ID for context management
            user_id: User ID for session management
            
        Returns:
            Generated response text
        """
        try:
            # 如果提供了session_id但没有conversation_history，从会话管理器获取历史
            if session_id and not conversation_history:
                conversation_history = session_manager.get_conversation_history(session_id)
            
            # 如果需要创建新会话
            if session_id and user_id and not session_manager._load_session(session_id):
                session_manager.create_session(user_id, session_id)
            
            # Build context prompt with emotional awareness
            context_prompt = self._build_context_prompt(emotion_context, conversation_history)
            
            # Generate response using OpenAI or mock
            if self.client and self.api_key:
                response_text = self._generate_openai_response(context_prompt, user_message)
            else:
                response_text = self._generate_mock_response(user_message, emotion_context)
            
            # 保存用户消息和AI回应到会话
            if session_id:
                # 保存用户消息
                user_msg = ConversationMessage(
                    role="user",
                    content=user_message,
                    timestamp=time.time()
                )
                session_manager.add_message(session_id, user_msg, emotion_context)
                
                # 保存AI回应
                ai_msg = ConversationMessage(
                    role="assistant", 
                    content=response_text,
                    timestamp=time.time()
                )
                session_manager.add_message(session_id, ai_msg)
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            raise Exception(f"Response generation failed: {str(e)}")
    
    def _build_context_prompt(
        self, 
        emotion_context: Optional[str], 
        conversation_history: Optional[List[ConversationMessage]]
    ) -> str:
        """Build context prompt with emotional awareness"""
        
        context_parts = [self.system_prompt]
        
        # Add emotional context
        if emotion_context:
            emotion_guidance = self._get_emotion_specific_guidance(emotion_context)
            context_parts.append(f"\nCurrent user emotion: {emotion_context}")
            context_parts.append(f"Emotional guidance: {emotion_guidance}")
        
        # Add conversation history
        if conversation_history:
            context_parts.append("\nRecent conversation:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role_prefix = "User" if msg.role == "user" else "Aura"
                context_parts.append(f"{role_prefix}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def _get_emotion_specific_guidance(self, emotion: str) -> str:
        """Get specific guidance for each emotion"""
        guidance = {
            "happy": "The user is feeling positive. Match their energy while being supportive.",
            "sad": "The user is feeling down. Be extra gentle, validating, and comforting.",
            "angry": "The user is feeling frustrated. Stay calm and help them process anger constructively.",
            "fear": "The user is feeling anxious. Be reassuring and help them feel safe.",
            "surprise": "The user is processing something unexpected. Help them work through it.",
            "disgust": "The user is feeling repulsed by something. Be understanding and supportive.",
            "neutral": "The user's emotional state is balanced. Maintain supportive engagement."
        }
        return guidance.get(emotion.lower(), guidance["neutral"])
    
    def _generate_openai_response(self, context_prompt: str, user_message: str) -> str:
        """Generate response using OpenAI GPT-4o"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": context_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            # Fallback to mock response
            return self._generate_mock_response(user_message, "neutral")
    
    def _generate_mock_response(self, user_message: str, emotion_context: Optional[str] = None) -> str:
        """Generate mock response based on emotion context"""
        emotion = emotion_context.lower() if emotion_context else "neutral"
        
        responses = {
            "happy": [
                "I can sense your positive energy! It's wonderful to see you feeling good. What's bringing you joy today?",
                "Your happiness is contagious! I'm so glad you're in a good place right now.",
                "It's beautiful to connect with you when you're feeling so uplifted. Tell me more about what's going well!"
            ],
            "sad": [
                "I can hear that you're going through a difficult time, and I want you to know that your feelings are completely valid.",
                "I'm here with you in this moment. Sometimes sadness needs to be felt and honored. You're not alone.",
                "It takes courage to reach out when you're feeling low. I'm grateful you're sharing this with me."
            ],
            "angry": [
                "I can sense your frustration, and it's okay to feel angry. Let's work through this together.",
                "Your anger is telling us something important. I'm here to help you process these intense feelings safely.",
                "I hear the strength in your emotions. Sometimes anger shows us what matters most to us."
            ],
            "fear": [
                "I can feel that you're experiencing some anxiety or fear right now. You're safe here with me.",
                "Fear can feel overwhelming, but you're showing incredible courage by reaching out. I'm here to support you.",
                "Let's take this one step at a time. You don't have to face your fears alone."
            ],
            "surprise": [
                "It sounds like something unexpected has happened! I'm here to help you process whatever you're experiencing.",
                "Life can certainly surprise us. How are you feeling about this new development?",
                "Change and surprises can be a lot to handle. I'm here to support you through this."
            ],
            "disgust": [
                "I can sense that something is really bothering you. Your feelings are completely understandable.",
                "Sometimes we encounter things that just don't sit right with us. I'm here to help you work through this.",
                "It's okay to feel repulsed or disgusted by certain situations. Let's talk about what's troubling you."
            ],
            "neutral": [
                "I'm here and ready to listen. How are you feeling today?",
                "Thank you for reaching out. What's on your mind right now?",
                "I'm glad you're here. What would you like to talk about?"
            ]
        }
        
        import random
        return random.choice(responses.get(emotion, responses["neutral"]))
    
    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            "status": "active" if self.client else "mock_mode",
            "api_configured": bool(self.api_key),
            "openai_available": OPENAI_AVAILABLE,
            "model": "gpt-4o",
            "personality": "Aura - Emotionally Intelligent Mental Wellness Companion"
        }
    
    def test_generation(self, test_message: str = "Hello Aura, how are you?") -> bool:
        """Test response generation functionality"""
        try:
            result = self.generate_response(test_message, "neutral")
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Response generation test failed: {e}")
            return False
