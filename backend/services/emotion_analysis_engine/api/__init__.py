from fastapi import APIRouter
from .routes import router as emotion_router
from .biometric_routes import router as biometric_router

# Create main router for emotion analysis engine
router = APIRouter()

# Include sub-routers
router.include_router(emotion_router, tags=["emotion"])
router.include_router(biometric_router, tags=["biometric"])