#!/usr/bin/env python3
"""
Database models for Trust Commit System
SQLModel-based models for receipts and chain anchors
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
import json


class Receipt(SQLModel, table=True):
    """
    Trust commit receipt model
    Stores off-chain session summaries with cryptographic commitments
    """
    __tablename__ = "receipts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, index=True, max_length=255)
    consent_id: str = Field(max_length=255)
    user_uid: str = Field(index=True, max_length=255)  # Internal UID, never on-chain
    
    # Model hashes as JSON
    model_hashes: Dict[str, str] = Field(sa_column=Column(JSON))
    
    risk_bucket: str = Field(max_length=10)  # low|med|high
    cost_cents: Optional[int] = Field(default=None)
    timestamp: int = Field(index=True)  # Unix timestamp
    
    # Cryptographic fields
    commit_hash: str = Field(max_length=64, index=True)  # Hex HMAC-SHA256
    signature: str = Field(max_length=128)  # Base64 Ed25519 signature
    
    # Chain anchoring
    agent_did: str = Field(max_length=255)
    tx_id: Optional[str] = Field(default=None, max_length=255, index=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = Field(default=0)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """
        Convert to summary dictionary for canonical JSON generation
        Excludes cryptographic and metadata fields
        """
        return {
            "session_id": self.session_id,
            "consent_id": self.consent_id,
            "user_uid": self.user_uid,
            "model_hashes": self.model_hashes,
            "risk_bucket": self.risk_bucket,
            "cost_cents": self.cost_cents,
            "timestamp": self.timestamp
        }


class ChainAnchor(SQLModel, table=True):
    """
    Chain anchor simulation model
    Stores simulated on-chain commits for testing
    """
    __tablename__ = "chain_anchors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tx_id: str = Field(unique=True, index=True, max_length=255)
    agent_did: str = Field(max_length=255)
    commit_hash: str = Field(max_length=64)
    timestamp: int = Field()
    cost_cents: Optional[int] = Field(default=None)
    
    # Simulation metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_simulated: bool = Field(default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "tx_id": self.tx_id,
            "agent_did": self.agent_did,
            "commit_hash": self.commit_hash,
            "timestamp": self.timestamp,
            "cost_cents": self.cost_cents
        }


class RetryQueue(SQLModel, table=True):
    """
    Retry queue for failed chain writes
    Simple background task management
    """
    __tablename__ = "retry_queue"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, max_length=255)
    receipt_id: int = Field(foreign_key="receipts.id")
    
    # Retry metadata
    attempts: int = Field(default=0)
    next_retry: datetime = Field(default_factory=datetime.utcnow)
    last_error: Optional[str] = Field(default=None, max_length=1000)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
