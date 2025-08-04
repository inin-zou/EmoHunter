"""
🤖 Conversation Engine API Routes

FastAPI routes for conversation generation and text-to-speech functionality.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from common.schemas.conversation import ConversationRequest, ConversationResponse, TalkRequest, TalkResponse
from common.schemas.base import HealthResponse
from common.utils.logger import get_service_logger
from ..services.gpt4o_client import GPT4oClient
from ..services.tts_client import TTSClient

logger = get_service_logger("conversation_api")
router = APIRouter()

# Global service instances
gpt_client = GPT4oClient()
tts_client = TTSClient()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        service_name="Conversation Engine",
        version="1.0.0",
        status="healthy"
    )


@router.post("/generate", response_model=ConversationResponse)
async def generate_conversation(request: ConversationRequest):
    """Generate conversation response based on user message and emotion context"""
    try:
        # Generate response using GPT-4o
        response_text = gpt_client.generate_response(
            user_message=request.message,
            emotion_context=request.emotion_context,
            conversation_history=request.conversation_history
        )
        
        return ConversationResponse(
            response_text=response_text,
            emotion_adapted=bool(request.emotion_context),
            message="Response generated successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/talk", response_model=TalkResponse)
async def text_to_speech(request: TalkRequest):
    """Convert text to speech with emotion-aware voice modulation"""
    try:
        # Synthesize speech using TTS client
        synthesis_result = tts_client.synthesize_speech(
            text=request.text,
            emotion=request.emotion,
            voice_settings=request.voice_settings
        )
        
        return TalkResponse(
            audio_data=synthesis_result["audio_data"],
            audio_format=synthesis_result["audio_format"],
            duration_seconds=synthesis_result.get("duration_seconds"),
            message="Speech synthesis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=TalkResponse)
async def chat_with_voice(request: ConversationRequest):
    """Generate conversation response and convert to speech in one call"""
    try:
        # Generate text response
        response_text = gpt_client.generate_response(
            user_message=request.message,
            emotion_context=request.emotion_context,
            conversation_history=request.conversation_history
        )
        
        # Convert to speech
        synthesis_result = tts_client.synthesize_speech(
            text=response_text,
            emotion=request.emotion_context
        )
        
        return TalkResponse(
            audio_data=synthesis_result["audio_data"],
            audio_format=synthesis_result["audio_format"],
            duration_seconds=synthesis_result.get("duration_seconds"),
            message=f"Chat response: {response_text}"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in chat with voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices():
    """Get available voice configurations"""
    try:
        voices = tts_client.get_available_voices()
        return {"success": True, "data": voices}
    except Exception as e:
        logger.error(f"❌ Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get conversation engine status"""
    try:
        gpt_status = gpt_client.get_status()
        tts_status = tts_client.get_status()
        
        return {
            "success": True,
            "data": {
                "gpt_client": gpt_status,
                "tts_client": tts_status
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_services():
    """Test both GPT and TTS services"""
    try:
        gpt_test = gpt_client.test_generation()
        tts_test = tts_client.test_synthesis()
        
        return {
            "success": True,
            "data": {
                "gpt_test_passed": gpt_test,
                "tts_test_passed": tts_test,
                "overall_status": "healthy" if gpt_test and tts_test else "degraded"
            }
        }
    except Exception as e:
        logger.error(f"❌ Error testing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))
