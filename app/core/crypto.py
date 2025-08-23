#!/usr/bin/env python3
"""
Cryptographic utilities for Trust Commit System
Implements HKDF, HMAC-SHA256, Ed25519 signing, and SHA256 hashing
"""

import hashlib
import hmac
import base64
import os
from typing import Dict, Any, Optional
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder


def hkdf_expand(master_key: bytes, info: bytes, length: int = 32) -> bytes:
    """
    HKDF-Expand implementation for deriving user-scoped secrets
    
    Args:
        master_key: Master key material (32 bytes)
        info: Context information (user_uid as bytes)
        length: Output key length (default 32 bytes)
        
    Returns:
        Derived key material
    """
    if len(master_key) < 32:
        raise ValueError("Master key must be at least 32 bytes")
    
    # Simple HKDF-Expand using HMAC-SHA256
    prk = master_key  # In production, use proper HKDF-Extract
    okm = b""
    counter = 1
    
    while len(okm) < length:
        h = hmac.new(prk, info + counter.to_bytes(1, 'big'), hashlib.sha256)
        okm += h.digest()
        counter += 1
    
    return okm[:length]


def derive_user_key(master_key: bytes, user_uid: str) -> bytes:
    """
    Derive user-scoped HMAC key using HKDF
    
    Args:
        master_key: Master key from environment
        user_uid: User identifier
        
    Returns:
        32-byte user-scoped key
    """
    info = f"emohunter_user_{user_uid}".encode('utf-8')
    return hkdf_expand(master_key, info, 32)


def hmac_sha256(key: bytes, data: bytes) -> str:
    """
    Compute HMAC-SHA256 and return hex string
    
    Args:
        key: HMAC key
        data: Data to authenticate
        
    Returns:
        Hex-encoded HMAC digest
    """
    h = hmac.new(key, data, hashlib.sha256)
    return h.hexdigest()


def sha256_json(data: Dict[str, Any]) -> str:
    """
    Compute SHA256 hash of JSON data
    
    Args:
        data: Dictionary to hash
        
    Returns:
        Hex-encoded SHA256 digest
    """
    from app.core.canonical import canonical_json
    canonical_bytes = canonical_json(data)
    return hashlib.sha256(canonical_bytes).hexdigest()


class Ed25519Signer:
    """Ed25519 digital signature operations"""
    
    def __init__(self, secret_key_b64: Optional[str] = None):
        """
        Initialize with base64-encoded secret key
        
        Args:
            secret_key_b64: Base64-encoded Ed25519 secret key
        """
        if secret_key_b64:
            secret_bytes = base64.b64decode(secret_key_b64)
            self.signing_key = SigningKey(secret_bytes)
        else:
            # Generate new key if none provided
            self.signing_key = SigningKey.generate()
        
        self.verify_key = self.signing_key.verify_key
    
    def sign(self, data: bytes) -> str:
        """
        Sign data with Ed25519
        
        Args:
            data: Data to sign
            
        Returns:
            Base64-encoded signature
        """
        signature = self.signing_key.sign(data, encoder=Base64Encoder)
        return signature.signature.decode('utf-8')
    
    def verify(self, data: bytes, signature_b64: str) -> bool:
        """
        Verify Ed25519 signature
        
        Args:
            data: Original data
            signature_b64: Base64-encoded signature
            
        Returns:
            True if signature is valid
        """
        try:
            signature_bytes = base64.b64decode(signature_b64)
            self.verify_key.verify(data, signature_bytes)
            return True
        except Exception:
            return False
    
    def get_public_key_b64(self) -> str:
        """Get base64-encoded public key"""
        return base64.b64encode(bytes(self.verify_key)).decode('utf-8')
    
    def get_secret_key_b64(self) -> str:
        """Get base64-encoded secret key"""
        return base64.b64encode(bytes(self.signing_key)).decode('utf-8')


def get_master_key() -> bytes:
    """
    Get master key from environment
    
    Returns:
        32-byte master key
        
    Raises:
        ValueError: If MASTER_KEY not set or invalid
    """
    master_key_b64 = os.getenv("MASTER_KEY")
    if not master_key_b64:
        raise ValueError("MASTER_KEY environment variable not set")
    
    try:
        master_key = base64.b64decode(master_key_b64)
        if len(master_key) != 32:
            raise ValueError("Master key must be exactly 32 bytes")
        return master_key
    except Exception as e:
        raise ValueError(f"Invalid MASTER_KEY format: {e}")


def get_agent_signer() -> Ed25519Signer:
    """
    Get Ed25519 signer from environment
    
    Returns:
        Configured Ed25519Signer
        
    Raises:
        ValueError: If AGENT_SK not set or invalid
    """
    agent_sk = os.getenv("AGENT_SK")
    if not agent_sk:
        raise ValueError("AGENT_SK environment variable not set")
    
    return Ed25519Signer(agent_sk)
