"""
Base Pydantic models for shared data structures
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()


class HealthResponse(BaseResponse):
    """Health check response"""
    service_name: str
    version: str
    status: str = "healthy"


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
