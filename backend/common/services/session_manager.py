"""
💾 会话存储管理器
Session Storage Manager for conversation context and history
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from common.utils.logger import get_service_logger
from common.schemas.conversation import ConversationMessage

logger = get_service_logger("session_manager")

class StorageBackend(Enum):
    """存储后端类型"""
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"

@dataclass
class SessionMetadata:
    """会话元数据"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    emotions_detected: List[str]
    total_duration: float  # 会话总时长(秒)

@dataclass
class ConversationSession:
    """完整的对话会话"""
    metadata: SessionMetadata
    messages: List[ConversationMessage]
    context_summary: Optional[str] = None  # AI生成的上下文摘要

class SessionManager:
    """
    💾 会话存储管理器
    
    负责管理用户对话会话的存储、检索和上下文维护
    """
    
    def __init__(self, backend: StorageBackend = StorageBackend.MEMORY, max_history_length: int = 20):
        """
        初始化会话管理器
        
        Args:
            backend: 存储后端类型
            max_history_length: 每个会话保留的最大消息数量
        """
        self.backend = backend
        self.max_history_length = max_history_length
        
        # 内存存储 (默认)
        self._memory_sessions: Dict[str, ConversationSession] = {}
        
        # 初始化存储后端
        self._init_backend()
        
        logger.info(f"💾 Session Manager initialized with {backend.value} backend")
    
    def _init_backend(self):
        """初始化存储后端"""
        if self.backend == StorageBackend.REDIS:
            try:
                import redis
                from common.config import settings
                self.redis_client = redis.Redis.from_url(
                    settings.redis_url or "redis://localhost:6379"
                )
                self.redis_client.ping()
                logger.info("✅ Redis backend connected")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed, falling back to memory: {e}")
                self.backend = StorageBackend.MEMORY
        
        elif self.backend == StorageBackend.DATABASE:
            # TODO: 实现数据库后端
            logger.warning("⚠️ Database backend not implemented, using memory")
            self.backend = StorageBackend.MEMORY
    
    def create_session(self, user_id: str, session_id: Optional[str] = None) -> str:
        """
        创建新的会话
        
        Args:
            user_id: 用户ID
            session_id: 可选的会话ID，如果不提供则自动生成
            
        Returns:
            会话ID
        """
        if not session_id:
            session_id = f"{user_id}_{int(time.time())}"
        
        now = datetime.now()
        metadata = SessionMetadata(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            message_count=0,
            emotions_detected=[],
            total_duration=0.0
        )
        
        session = ConversationSession(
            metadata=metadata,
            messages=[]
        )
        
        self._store_session(session)
        logger.info(f"🆕 Created new session: {session_id} for user: {user_id}")
        
        return session_id
    
    def add_message(
        self, 
        session_id: str, 
        message: ConversationMessage,
        detected_emotion: Optional[str] = None
    ) -> bool:
        """
        向会话添加消息
        
        Args:
            session_id: 会话ID
            message: 对话消息
            detected_emotion: 检测到的情绪
            
        Returns:
            是否成功添加
        """
        try:
            session = self._load_session(session_id)
            if not session:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return False
            
            # 添加消息
            session.messages.append(message)
            
            # 更新元数据
            session.metadata.last_activity = datetime.now()
            session.metadata.message_count += 1
            
            # 记录检测到的情绪
            if detected_emotion and detected_emotion not in session.metadata.emotions_detected:
                session.metadata.emotions_detected.append(detected_emotion)
            
            # 限制历史长度
            if len(session.messages) > self.max_history_length:
                # 保留最近的消息，但生成上下文摘要
                old_messages = session.messages[:-self.max_history_length]
                session.messages = session.messages[-self.max_history_length:]
                
                # 生成上下文摘要 (简化版)
                session.context_summary = self._generate_context_summary(old_messages)
            
            # 存储更新后的会话
            self._store_session(session)
            
            logger.debug(f"📝 Added message to session {session_id}: {message.role}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add message to session {session_id}: {e}")
            return False
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            limit: 限制返回的消息数量
            
        Returns:
            对话消息列表
        """
        try:
            session = self._load_session(session_id)
            if not session:
                return []
            
            messages = session.messages
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation history for {session_id}: {e}")
            return []
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话上下文信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话上下文字典
        """
        try:
            session = self._load_session(session_id)
            if not session:
                return {}
            
            # 计算会话持续时间
            duration = (session.metadata.last_activity - session.metadata.created_at).total_seconds()
            session.metadata.total_duration = duration
            
            return {
                "session_id": session_id,
                "user_id": session.metadata.user_id,
                "message_count": session.metadata.message_count,
                "emotions_detected": session.metadata.emotions_detected,
                "session_duration": duration,
                "last_activity": session.metadata.last_activity.isoformat(),
                "context_summary": session.context_summary,
                "recent_messages": len(session.messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session context for {session_id}: {e}")
            return {}
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        清理过期会话
        
        Args:
            max_age_hours: 会话最大保留时间(小时)
            
        Returns:
            清理的会话数量
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            if self.backend == StorageBackend.MEMORY:
                expired_sessions = []
                for session_id, session in self._memory_sessions.items():
                    if session.metadata.last_activity < cutoff_time:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self._memory_sessions[session_id]
                    cleaned_count += 1
            
            # TODO: 实现Redis和数据库的清理逻辑
            
            if cleaned_count > 0:
                logger.info(f"🧹 Cleaned up {cleaned_count} expired sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired sessions: {e}")
            return 0
    
    def _store_session(self, session: ConversationSession):
        """存储会话到后端"""
        session_id = session.metadata.session_id
        
        if self.backend == StorageBackend.MEMORY:
            self._memory_sessions[session_id] = session
        
        elif self.backend == StorageBackend.REDIS:
            try:
                session_data = {
                    "metadata": asdict(session.metadata),
                    "messages": [asdict(msg) for msg in session.messages],
                    "context_summary": session.context_summary
                }
                # 转换datetime为字符串
                session_data["metadata"]["created_at"] = session.metadata.created_at.isoformat()
                session_data["metadata"]["last_activity"] = session.metadata.last_activity.isoformat()
                
                self.redis_client.setex(
                    f"session:{session_id}",
                    86400,  # 24小时过期
                    json.dumps(session_data, ensure_ascii=False)
                )
            except Exception as e:
                logger.error(f"❌ Failed to store session to Redis: {e}")
                # 回退到内存存储
                self._memory_sessions[session_id] = session
    
    def _load_session(self, session_id: str) -> Optional[ConversationSession]:
        """从后端加载会话"""
        try:
            if self.backend == StorageBackend.MEMORY:
                return self._memory_sessions.get(session_id)
            
            elif self.backend == StorageBackend.REDIS:
                try:
                    data = self.redis_client.get(f"session:{session_id}")
                    if not data:
                        return None
                    
                    session_data = json.loads(data)
                    
                    # 重构会话对象
                    metadata = SessionMetadata(
                        session_id=session_data["metadata"]["session_id"],
                        user_id=session_data["metadata"]["user_id"],
                        created_at=datetime.fromisoformat(session_data["metadata"]["created_at"]),
                        last_activity=datetime.fromisoformat(session_data["metadata"]["last_activity"]),
                        message_count=session_data["metadata"]["message_count"],
                        emotions_detected=session_data["metadata"]["emotions_detected"],
                        total_duration=session_data["metadata"]["total_duration"]
                    )
                    
                    messages = [
                        ConversationMessage(**msg_data) 
                        for msg_data in session_data["messages"]
                    ]
                    
                    return ConversationSession(
                        metadata=metadata,
                        messages=messages,
                        context_summary=session_data.get("context_summary")
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load session from Redis: {e}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to load session {session_id}: {e}")
            return None
    
    def _generate_context_summary(self, old_messages: List[ConversationMessage]) -> str:
        """生成上下文摘要 (简化版)"""
        try:
            # 简单的摘要生成逻辑
            user_messages = [msg for msg in old_messages if msg.role == "user"]
            ai_messages = [msg for msg in old_messages if msg.role == "assistant"]
            
            summary_parts = []
            
            if user_messages:
                summary_parts.append(f"用户提到了{len(user_messages)}个话题")
            
            if ai_messages:
                summary_parts.append(f"AI提供了{len(ai_messages)}次回应")
            
            # 提取关键词 (简化版)
            all_content = " ".join([msg.content for msg in old_messages])
            if "工作" in all_content:
                summary_parts.append("讨论了工作相关话题")
            if "情绪" in all_content or "感觉" in all_content:
                summary_parts.append("涉及情绪和感受")
            
            return "早期对话: " + ", ".join(summary_parts) if summary_parts else "早期对话内容"
            
        except Exception as e:
            logger.error(f"❌ Failed to generate context summary: {e}")
            return "早期对话内容"
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        if self.backend == StorageBackend.MEMORY:
            return len(self._memory_sessions)
        # TODO: 实现其他后端的统计
        return 0
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """获取用户的所有会话ID"""
        sessions = []
        
        if self.backend == StorageBackend.MEMORY:
            for session_id, session in self._memory_sessions.items():
                if session.metadata.user_id == user_id:
                    sessions.append(session_id)
        
        return sessions

# 全局会话管理器实例
session_manager = SessionManager()
