"""
Logging utilities for all services
"""

import logging
import sys
from typing import Optional
from ..config import settings


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Setup logger with consistent formatting across services"""
    
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler if not already exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(settings.log_format)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


def get_service_logger(service_name: str) -> logging.Logger:
    """Get logger for a specific service"""
    return setup_logger(f"emohunter.{service_name}")
