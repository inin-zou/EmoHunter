"""
EmoHunter Incentive Engine - Smart Contract Interface

This module provides a Python interface to interact with the EmoHunterIncentiveEngine
smart contract deployed on the blockchain.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import logging

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    HAPPY = 0
    SAD = 1
    ANGRY = 2
    SURPRISED = 3
    FEARFUL = 4
    DISGUSTED = 5
    NEUTRAL = 6

class RewardTier(Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3

class IncentiveEngineInterface:
    """
    Interface to interact with the EmoHunterIncentiveEngine smart contract
    """
    
    def __init__(self, 
                 web3_provider_url: str,
                 contract_address: str,
                 contract_abi: List[Dict],
                 private_key: str):
        """
        Initialize the contract interface
        
        Args:
            web3_provider_url: URL of the Web3 provider (e.g., Infura, Alchemy)
            contract_address: Address of the deployed contract
            contract_abi: ABI of the contract
            private_key: Private key of the authorized backend account
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.account = Account.from_key(private_key)
        self.contract_address = Web3.to_checksum_address(contract_address)
        
        # Initialize contract
        self.contract: Contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=contract_abi
        )
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Web3 provider")
        
        logger.info(f"Connected to contract at {self.contract_address}")
    
    def start_session(self, user_address: str) -> Tuple[bool, Optional[int]]:
        """
        Start a new user session
        
        Args:
            user_address: Ethereum address of the user
            
        Returns:
            Tuple of (success, session_id)
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            # Build transaction
            transaction = self.contract.functions.startSession(user_address).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Parse logs to get session ID
                session_started_event = self.contract.events.SessionStarted().process_receipt(receipt)
                if session_started_event:
                    session_id = session_started_event[0]['args']['sessionId']
                    logger.info(f"Started session {session_id} for user {user_address}")
                    return True, session_id
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return False, None
    
    def record_emotion(self, 
                      user_address: str, 
                      session_id: int, 
                      emotion: EmotionType, 
                      duration: int) -> bool:
        """
        Record emotion data for a user session
        
        Args:
            user_address: Ethereum address of the user
            session_id: Session identifier
            emotion: Type of emotion detected
            duration: Duration of the emotion in milliseconds
            
        Returns:
            Success status
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            transaction = self.contract.functions.recordEmotion(
                user_address,
                session_id,
                emotion.value,
                duration
            ).build_transaction({
                'from': self.account.address,
                'gas': 150000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Recorded {emotion.name} emotion for user {user_address}, session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error recording emotion: {e}")
            return False
    
    def end_session(self, user_address: str, session_id: int) -> bool:
        """
        End a user session and calculate rewards
        
        Args:
            user_address: Ethereum address of the user
            session_id: Session identifier
            
        Returns:
            Success status
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            transaction = self.contract.functions.endSession(
                user_address,
                session_id
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Ended session {session_id} for user {user_address}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    def get_user_session(self, user_address: str, session_id: int) -> Optional[Dict]:
        """
        Get session data for a user
        
        Args:
            user_address: Ethereum address of the user
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            result = self.contract.functions.getUserSession(
                user_address,
                session_id
            ).call()
            
            return {
                'start_time': result[0],
                'end_time': result[1],
                'total_engagement_score': result[2],
                'tier': RewardTier(result[3]).name,
                'reward_claimed': result[4]
            }
            
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None
    
    def get_emotion_data(self, 
                        user_address: str, 
                        session_id: int, 
                        emotion: EmotionType) -> Optional[Dict]:
        """
        Get emotion data for a specific emotion type in a session
        
        Args:
            user_address: Ethereum address of the user
            session_id: Session identifier
            emotion: Emotion type to query
            
        Returns:
            Emotion data dictionary or None
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            result = self.contract.functions.getEmotionData(
                user_address,
                session_id,
                emotion.value
            ).call()
            
            return {
                'count': result[0],
                'duration': result[1]
            }
            
        except Exception as e:
            logger.error(f"Error getting emotion data: {e}")
            return None
    
    def calculate_pending_reward(self, user_address: str, session_id: int) -> Optional[int]:
        """
        Calculate pending reward for a session
        
        Args:
            user_address: Ethereum address of the user
            session_id: Session identifier
            
        Returns:
            Reward amount in wei or None
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            result = self.contract.functions.calculatePendingReward(
                user_address,
                session_id
            ).call()
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating pending reward: {e}")
            return None
    
    def get_user_session_count(self, user_address: str) -> Optional[int]:
        """
        Get the total number of sessions for a user
        
        Args:
            user_address: Ethereum address of the user
            
        Returns:
            Session count or None
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            result = self.contract.functions.userSessionCount(user_address).call()
            return result
            
        except Exception as e:
            logger.error(f"Error getting user session count: {e}")
            return None
    
    def get_total_user_rewards(self, user_address: str) -> Optional[int]:
        """
        Get total rewards earned by a user
        
        Args:
            user_address: Ethereum address of the user
            
        Returns:
            Total rewards in wei or None
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            
            result = self.contract.functions.totalUserRewards(user_address).call()
            return result
            
        except Exception as e:
            logger.error(f"Error getting total user rewards: {e}")
            return None

class IncentiveEngineManager:
    """
    High-level manager for the incentive engine
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the incentive engine manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.interface = None
        self._initialize_interface()
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from file or environment variables"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Load from environment variables
        return {
            'web3_provider_url': os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545'),
            'contract_address': os.getenv('INCENTIVE_CONTRACT_ADDRESS'),
            'private_key': os.getenv('BACKEND_PRIVATE_KEY'),
            'contract_abi_path': os.getenv('CONTRACT_ABI_PATH', './contracts/out/EmoHunterIncentiveEngine.sol/EmoHunterIncentiveEngine.json')
        }
    
    def _initialize_interface(self):
        """Initialize the contract interface"""
        try:
            # Load contract ABI
            abi_path = self.config['contract_abi_path']
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_data = json.load(f)
                    abi = contract_data.get('abi', [])
            else:
                logger.warning(f"ABI file not found at {abi_path}")
                abi = []
            
            self.interface = IncentiveEngineInterface(
                web3_provider_url=self.config['web3_provider_url'],
                contract_address=self.config['contract_address'],
                contract_abi=abi,
                private_key=self.config['private_key']
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize incentive engine interface: {e}")
    
    def process_emotion_session(self, 
                               user_address: str, 
                               emotions_data: List[Dict]) -> Optional[int]:
        """
        Process a complete emotion session
        
        Args:
            user_address: Ethereum address of the user
            emotions_data: List of emotion data dictionaries with keys:
                          - emotion: EmotionType
                          - duration: int (milliseconds)
                          - timestamp: int (unix timestamp)
        
        Returns:
            Session ID if successful, None otherwise
        """
        if not self.interface:
            logger.error("Interface not initialized")
            return None
        
        # Start session
        success, session_id = self.interface.start_session(user_address)
        if not success or session_id is None:
            logger.error("Failed to start session")
            return None
        
        # Record all emotions
        for emotion_data in emotions_data:
            emotion = EmotionType[emotion_data['emotion'].upper()]
            duration = emotion_data['duration']
            
            success = self.interface.record_emotion(
                user_address, session_id, emotion, duration
            )
            if not success:
                logger.warning(f"Failed to record emotion {emotion.name}")
        
        # End session
        success = self.interface.end_session(user_address, session_id)
        if not success:
            logger.error("Failed to end session")
            return None
        
        logger.info(f"Successfully processed emotion session {session_id} for user {user_address}")
        return session_id
    
    def get_user_stats(self, user_address: str) -> Optional[Dict]:
        """
        Get comprehensive user statistics
        
        Args:
            user_address: Ethereum address of the user
            
        Returns:
            User statistics dictionary
        """
        if not self.interface:
            return None
        
        session_count = self.interface.get_user_session_count(user_address)
        total_rewards = self.interface.get_total_user_rewards(user_address)
        
        if session_count is None or total_rewards is None:
            return None
        
        return {
            'user_address': user_address,
            'total_sessions': session_count,
            'total_rewards': total_rewards,
            'average_reward_per_session': total_rewards / max(session_count, 1)
        }

# Factory function for easy initialization
def create_incentive_engine(config_path: str = None) -> IncentiveEngineManager:
    """
    Factory function to create an incentive engine manager
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Initialized IncentiveEngineManager instance
    """
    return IncentiveEngineManager(config_path)
