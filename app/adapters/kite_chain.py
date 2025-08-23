#!/usr/bin/env python3
"""
Kite Chain Adapter for Trust Commit System
Handles on-chain commitment anchoring with simulation support
"""

import os
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.db.models import ChainAnchor
from app.db.session import get_async_session


logger = logging.getLogger(__name__)


class KiteChainAdapter:
    """
    Adapter for KiteAI blockchain integration
    Supports both simulation mode and real chain deployment
    """
    
    def __init__(self):
        self.chain_enabled = os.getenv("CHAIN_ENABLED", "false").lower() == "true"
        self.kite_api_key = os.getenv("KITE_API_KEY")
        self.agent_service_id = os.getenv("KITE_AGENT_SERVICE_ID")
        self.agent_did = os.getenv("AGENT_DID", "did:kite:emohunter")
        
        # Initialize KiteAI client if real chain is enabled
        if self.chain_enabled and self.kite_api_key:
            try:
                from kite_sdk import KiteClient
                self.kite_client = KiteClient(api_key=self.kite_api_key)
                logger.info("KiteAI client initialized successfully")
            except ImportError:
                logger.warning("kite_sdk not installed, falling back to simulation mode")
                self.chain_enabled = False
                self.kite_client = None
            except Exception as e:
                logger.error(f"Failed to initialize KiteAI client: {e}")
                self.chain_enabled = False
                self.kite_client = None
        else:
            self.kite_client = None
            
        # Fallback to simulation storage
        self._simulated_commits: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"KiteChainAdapter initialized: chain_enabled={self.chain_enabled}")
    
    async def write_commit(
        self, 
        agent_did: str, 
        commit_hash: str, 
        timestamp: int, 
        cost_cents: Optional[int] = None
    ) -> str:
        """
        Write commitment to KiteAI chain or simulate
        
        Args:
            agent_did: Agent DID (e.g., "did:kite:emohunter")
            commit_hash: HMAC-SHA256 commitment hash
            timestamp: Unix timestamp
            cost_cents: Optional cost in cents
            
        Returns:
            Transaction ID or simulated ID
        """
        if self.chain_enabled and self.kite_client:
            return await self._write_to_kite_chain({
                "agent_did": agent_did,
                "commit_hash": commit_hash,
                "timestamp": timestamp,
                "cost_cents": cost_cents
            })
        else:
            return await self._simulate_write_commit(
                agent_did, commit_hash, timestamp, cost_cents
            )
    
    async def _write_to_kite_chain(self, commit_data: dict) -> str:
        """Write commitment to real KiteAI blockchain"""
        try:
            # Prepare commitment payload for KiteAI
            kite_payload = {
                "agent_did": commit_data.get("agent_did"),
                "commit_hash": commit_data.get("commit_hash"),
                "timestamp": commit_data.get("timestamp"),
                "cost_cents": commit_data.get("cost_cents", 0)
            }
            
            # Call KiteAI service to anchor commitment
            response = self.kite_client.call_service(
                service_id=self.agent_service_id,
                inputs={"action": "anchor_commitment", "data": kite_payload}
            )
            
            # Extract transaction ID from response
            tx_id = response.get("transaction_id") or response.get("tx_id")
            
            if not tx_id:
                raise Exception("No transaction ID returned from KiteAI")
                
            logger.info(f"Successfully anchored commitment on KiteAI chain: {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to write to KiteAI chain: {e}")
            # Store in retry queue for later processing
            await self._store_retry_entry(commit_data, str(e))
            return "pending"
    
    async def get_commit(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve commitment from KiteAI blockchain or simulate
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Commitment data or None
        """
        if self.chain_enabled and self.kite_client:
            return await self._get_from_kite_chain(tx_id)
        else:
            return await self._simulate_get_commit(tx_id)
    
    async def _get_from_kite_chain(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve commitment from real KiteAI blockchain"""
        try:
            # Call KiteAI service to retrieve commitment
            response = self.kite_client.call_service(
                service_id=self.agent_service_id,
                inputs={"action": "get_commitment", "data": {"tx_id": tx_id}}
            )
            
            # Extract commitment data from response
            commit_data = response.get("commitment")
            
            if not commit_data:
                raise Exception("No commitment data returned from KiteAI")
                
            logger.info(f"Successfully retrieved commitment from KiteAI chain: {tx_id}")
            return commit_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve from KiteAI chain: {e}")
            return None
    
    async def _simulate_write_commit(
        self,
        agent_did: str,
        commit_hash: str, 
        timestamp: int,
        cost_cents: Optional[int] = None
    ) -> str:
        """
        Simulate blockchain write operation
        
        Returns:
            Simulated transaction ID
        """
        # Generate simulated transaction ID
        tx_id = f"tx_sim_{uuid.uuid4().hex[:16]}"
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Store in simulated chain (in-memory)
        commit_data = {
            "agent_did": agent_did,
            "commit_hash": commit_hash,
            "timestamp": timestamp,
            "cost_cents": cost_cents,
            "anchored_at": int(datetime.utcnow().timestamp())
        }
        
        self._simulated_commits[tx_id] = commit_data
        
        # Also store in database for persistence
        async for session in get_async_session():
            anchor = ChainAnchor(
                tx_id=tx_id,
                agent_did=agent_did,
                commit_hash=commit_hash,
                timestamp=timestamp,
                cost_cents=cost_cents,
                is_simulated=True
            )
            session.add(anchor)
            await session.commit()
            break
        
        logger.info(f"Simulated chain write: tx_id={tx_id}, commit_hash={commit_hash}")
        return tx_id
    
    async def _simulate_get_commit(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Simulate blockchain read operation
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Simulated commitment data or None
        """
        # Check in-memory storage first
        if tx_id in self._simulated_commits:
            return self._simulated_commits[tx_id]
        
        # Check database for persistence
        async for session in get_async_session():
            anchor = await session.get(ChainAnchor, tx_id)
            if anchor:
                return anchor.to_dict()
            break
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check adapter health and connectivity
        
        Returns:
            Health status information
        """
        return {
            "status": "healthy",
            "chain_enabled": self.chain_enabled,
            "agent_did": self.agent_did,
            "mode": "simulation" if not self.chain_enabled else "real",
            "simulated_commits": len(self._simulated_commits)
        }


# Global adapter instance
kite_adapter = KiteChainAdapter()


async def write_commit(
    agent_did: str,
    commit_hash: str, 
    timestamp: int,
    cost_cents: Optional[int] = None
) -> str:
    """
    Convenience function for writing commits
    
    Args:
        agent_did: Agent DID
        commit_hash: Commitment hash
        timestamp: Unix timestamp
        cost_cents: Optional cost
        
    Returns:
        Transaction ID
    """
    return await kite_adapter.write_commit(
        agent_did, commit_hash, timestamp, cost_cents
    )


async def get_commit(tx_id: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function for retrieving commits
    
    Args:
        tx_id: Transaction ID
        
    Returns:
        Commitment data or None
    """
    return await kite_adapter.get_commit(tx_id)
