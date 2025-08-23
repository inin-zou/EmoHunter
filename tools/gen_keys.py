#!/usr/bin/env python3
"""
Key generation utility for Trust Commit System
Generates Ed25519 keypair and master key for HKDF
"""

import os
import base64
import secrets
from nacl.signing import SigningKey


def generate_master_key() -> str:
    """
    Generate a secure 32-byte master key for HKDF
    
    Returns:
        Base64-encoded master key
    """
    master_key = secrets.token_bytes(32)
    return base64.b64encode(master_key).decode('utf-8')


def generate_ed25519_keypair() -> tuple[str, str]:
    """
    Generate Ed25519 signing keypair
    
    Returns:
        Tuple of (secret_key_b64, public_key_b64)
    """
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    
    secret_key_b64 = base64.b64encode(bytes(signing_key)).decode('utf-8')
    public_key_b64 = base64.b64encode(bytes(verify_key)).decode('utf-8')
    
    return secret_key_b64, public_key_b64


def main():
    """Generate and print all required keys"""
    print("🔐 EmoHunter Trust Commit System - Key Generation")
    print("=" * 60)
    
    # Generate master key for HKDF
    master_key = generate_master_key()
    print(f"MASTER_KEY={master_key}")
    
    # Generate Ed25519 keypair
    secret_key, public_key = generate_ed25519_keypair()
    print(f"AGENT_SK={secret_key}")
    print(f"AGENT_PK={public_key}")
    
    # Default configuration
    print(f"AGENT_DID=did:kite:emohunter")
    print(f"CHAIN_ENABLED=false")
    
    print("\n" + "=" * 60)
    print("💡 Copy these values to your .env file:")
    print("=" * 60)
    print(f"""
# Trust Commit System Configuration
MASTER_KEY={master_key}
AGENT_SK={secret_key}
AGENT_DID=did:kite:emohunter
CHAIN_ENABLED=false

# Database
DATABASE_URL=sqlite:///./trust_commit.db
""")


if __name__ == "__main__":
    main()
