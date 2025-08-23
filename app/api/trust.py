#!/usr/bin/env python3
"""
Trust Commit API endpoints
Implements POST /trust/commit and GET /trust/verify
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.crypto import (
    get_master_key, derive_user_key, hmac_sha256, 
    get_agent_signer, sha256_json
)
from app.core.canonical import canonical_json
from app.db.models import Receipt, RetryQueue
from app.db.session import get_async_session
from app.adapters.kite_chain import write_commit, get_commit


logger = logging.getLogger(__name__)
router = APIRouter()


class CommitRequest(BaseModel):
    """Request model for POST /trust/commit"""
    session_id: str = Field(..., max_length=255)
    consent_id: str = Field(..., max_length=255)
    user_uid: str = Field(..., max_length=255)
    model_hashes: Dict[str, str] = Field(...)
    risk_bucket: str = Field(..., pattern="^(low|med|high)$")
    cost_cents: Optional[int] = Field(None, ge=0)
    timestamp: int = Field(..., gt=0)


class CommitResponse(BaseModel):
    """Response model for POST /trust/commit"""
    commit_hash: str
    tx_id: str
    agent_did: str
    signature: str
    anchored_at: int


class VerifyResponse(BaseModel):
    """Response model for GET /trust/verify"""
    match: bool
    agent_did: str
    anchored_at: int
    details: Optional[Dict[str, Any]] = None


@router.post("/commit", response_model=CommitResponse)
async def create_trust_commit(
    request: CommitRequest,
    session: Session = Depends(get_async_session)
) -> CommitResponse:
    """
    Create a trust commitment for a session
    
    Process:
    1. Validate and canonicalize summary
    2. Compute HMAC commitment hash
    3. Sign with Ed25519
    4. Write to chain (async)
    5. Store receipt
    """
    try:
        # Check for existing receipt (idempotency)
        existing_receipt = await session.exec(
            select(Receipt).where(Receipt.session_id == request.session_id)
        ).first()
        
        if existing_receipt:
            logger.info(f"Returning existing receipt for session {request.session_id}")
            return CommitResponse(
                commit_hash=existing_receipt.commit_hash,
                tx_id=existing_receipt.tx_id or "pending",
                agent_did=existing_receipt.agent_did,
                signature=existing_receipt.signature,
                anchored_at=existing_receipt.timestamp
            )
        
        # Validate model_hashes presence
        if not request.model_hashes:
            raise HTTPException(status_code=400, detail="model_hashes cannot be empty")
        
        # Create summary for commitment
        summary_data = {
            "session_id": request.session_id,
            "consent_id": request.consent_id,
            "user_uid": request.user_uid,
            "model_hashes": request.model_hashes,
            "risk_bucket": request.risk_bucket,
            "cost_cents": request.cost_cents,
            "timestamp": request.timestamp
        }
        
        # Canonicalize summary
        canonical_summary = canonical_json(summary_data)
        
        # Derive user-scoped HMAC key
        master_key = get_master_key()
        user_key = derive_user_key(master_key, request.user_uid)
        
        # Compute commitment hash
        commit_hash = hmac_sha256(user_key, canonical_summary)
        
        # Prepare signature data: commit_hash || hash(model_hashes)
        model_hashes_hash = sha256_json(request.model_hashes)
        signature_data = (commit_hash + model_hashes_hash).encode('utf-8')
        
        # Sign with Ed25519
        signer = get_agent_signer()
        signature = signer.sign(signature_data)
        
        # Get agent DID
        agent_did = os.getenv("AGENT_DID", "did:kite:emohunter")
        
        # Write to chain (async)
        try:
            tx_id = await write_commit(
                agent_did=agent_did,
                commit_hash=commit_hash,
                timestamp=request.timestamp,
                cost_cents=request.cost_cents
            )
        except Exception as e:
            logger.error(f"Chain write failed: {e}")
            tx_id = None  # Will be retried later
        
        # Create and store receipt
        receipt = Receipt(
            session_id=request.session_id,
            consent_id=request.consent_id,
            user_uid=request.user_uid,
            model_hashes=request.model_hashes,
            risk_bucket=request.risk_bucket,
            cost_cents=request.cost_cents,
            timestamp=request.timestamp,
            commit_hash=commit_hash,
            signature=signature,
            agent_did=agent_did,
            tx_id=tx_id
        )
        
        session.add(receipt)
        await session.commit()
        await session.refresh(receipt)
        
        # If chain write failed, add to retry queue
        if tx_id is None:
            retry_entry = RetryQueue(
                session_id=request.session_id,
                receipt_id=receipt.id,
                attempts=0,
                last_error="Initial chain write failed"
            )
            session.add(retry_entry)
            await session.commit()
            tx_id = "pending"
        
        logger.info(f"Trust commit created: session={request.session_id}, hash={commit_hash}")
        
        return CommitResponse(
            commit_hash=commit_hash,
            tx_id=tx_id,
            agent_did=agent_did,
            signature=signature,
            anchored_at=request.timestamp
        )
        
    except Exception as e:
        logger.error(f"Trust commit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")


@router.get("/verify", response_model=VerifyResponse)
async def verify_trust_commit(
    tx_id: str = Query(..., description="Transaction ID"),
    session_id: str = Query(..., description="Session ID"),
    session: Session = Depends(get_async_session)
) -> VerifyResponse:
    """
    Verify a trust commitment
    
    Process:
    1. Load receipt by session_id
    2. Rebuild canonical JSON and recompute HMAC
    3. Check chain anchor matches
    4. Verify Ed25519 signature
    """
    try:
        # Load receipt
        receipt = await session.exec(
            select(Receipt).where(Receipt.session_id == session_id)
        ).first()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        # Rebuild canonical summary and recompute HMAC
        summary_data = receipt.to_summary_dict()
        canonical_summary = canonical_json(summary_data)
        
        master_key = get_master_key()
        user_key = derive_user_key(master_key, receipt.user_uid)
        expected_commit_hash = hmac_sha256(user_key, canonical_summary)
        
        # Check local hash matches
        local_hash_match = expected_commit_hash == receipt.commit_hash
        
        # Check chain anchor
        chain_commit = await get_commit(tx_id)
        chain_hash_match = False
        anchored_at = receipt.timestamp
        
        if chain_commit:
            chain_hash_match = chain_commit["commit_hash"] == receipt.commit_hash
            anchored_at = chain_commit.get("timestamp", receipt.timestamp)
        
        # Verify signature
        model_hashes_hash = sha256_json(receipt.model_hashes)
        signature_data = (receipt.commit_hash + model_hashes_hash).encode('utf-8')
        
        signer = get_agent_signer()
        signature_valid = signer.verify(signature_data, receipt.signature)
        
        # Overall match
        overall_match = local_hash_match and signature_valid
        if chain_commit:
            overall_match = overall_match and chain_hash_match
        
        logger.info(f"Verification: session={session_id}, match={overall_match}")
        
        return VerifyResponse(
            match=overall_match,
            agent_did=receipt.agent_did,
            anchored_at=anchored_at,
            details={
                "local_hash_match": local_hash_match,
                "chain_hash_match": chain_hash_match,
                "signature_valid": signature_valid,
                "chain_found": chain_commit is not None,
                "tx_id": tx_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/health")
async def trust_health():
    """Health check for trust system"""
    try:
        # Test crypto operations
        master_key = get_master_key()
        signer = get_agent_signer()
        
        return {
            "status": "healthy",
            "crypto": "ok",
            "agent_did": os.getenv("AGENT_DID", "did:kite:emohunter"),
            "chain_enabled": os.getenv("CHAIN_ENABLED", "false").lower() == "true"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
