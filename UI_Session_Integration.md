# 💾 UI会话存储集成指南

## 🎯 实现目标

让语音助手能够记住之前的对话内容，实现真正的上下文感知对话：

```
用户: "我今天很焦虑，明天有面试"
AI: "我理解你的焦虑，面试确实让人紧张..."

[几分钟后]
用户: "那个面试的事，你觉得我还需要准备什么？"
AI: "基于我们刚才的对话，我记得你明天有面试并且感到焦虑..."
```

## 🏗️ 架构设计

### 会话存储层级
```
📱 UI层
  ↓ session_id + user_id
🌐 API网关层  
  ↓ 转发会话信息
🤖 对话引擎
  ↓ 自动获取历史
💾 会话管理器
  ↓ 存储/检索
🗄️ 存储后端 (内存/Redis/数据库)
```

## 🚀 前端实现

### 1. 会话管理Hook (React)

```jsx
// hooks/useSessionManager.js
import { useState, useEffect, useCallback } from 'react';

export const useSessionManager = (userId) => {
    const [sessionId, setSessionId] = useState(null);
    const [sessionContext, setSessionContext] = useState({});
    const [isLoading, setIsLoading] = useState(false);

    // 创建或恢复会话
    const initializeSession = useCallback(async () => {
        try {
            setIsLoading(true);
            
            // 尝试从localStorage恢复会话
            const savedSessionId = localStorage.getItem(`session_${userId}`);
            
            if (savedSessionId) {
                // 验证会话是否仍然有效
                const response = await fetch(`/api/v1/session/${savedSessionId}/context`);
                if (response.ok) {
                    setSessionId(savedSessionId);
                    const context = await response.json();
                    setSessionContext(context);
                    console.log('✅ 会话已恢复:', savedSessionId);
                    return savedSessionId;
                }
            }
            
            // 创建新会话
            const response = await fetch('/api/v1/session/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            
            const { session_id } = await response.json();
            setSessionId(session_id);
            localStorage.setItem(`session_${userId}`, session_id);
            console.log('🆕 新会话已创建:', session_id);
            
            return session_id;
            
        } catch (error) {
            console.error('❌ 会话初始化失败:', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [userId]);

    // 发送上下文感知消息
    const sendContextAwareMessage = useCallback(async (message, emotion = null) => {
        if (!sessionId) {
            console.error('❌ 会话未初始化');
            return null;
        }

        try {
            const response = await fetch('/api/v1/unified/emotion_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    user_id: userId,
                    session_id: sessionId,
                    emotion_context: emotion,
                    include_emotion: true,
                    include_voice: true,
                    use_session_context: true  // 关键：启用会话上下文
                })
            });

            const result = await response.json();
            
            // 更新会话上下文
            if (result.session_context) {
                setSessionContext(result.session_context);
            }

            return result;
            
        } catch (error) {
            console.error('❌ 发送消息失败:', error);
            return null;
        }
    }, [sessionId, userId]);

    // 获取对话历史
    const getConversationHistory = useCallback(async (limit = 10) => {
        if (!sessionId) return [];

        try {
            const response = await fetch(`/api/v1/session/${sessionId}/history?limit=${limit}`);
            return await response.json();
        } catch (error) {
            console.error('❌ 获取历史失败:', error);
            return [];
        }
    }, [sessionId]);

    // 清除会话
    const clearSession = useCallback(() => {
        localStorage.removeItem(`session_${userId}`);
        setSessionId(null);
        setSessionContext({});
    }, [userId]);

    useEffect(() => {
        if (userId) {
            initializeSession();
        }
    }, [userId, initializeSession]);

    return {
        sessionId,
        sessionContext,
        isLoading,
        sendContextAwareMessage,
        getConversationHistory,
        clearSession,
        initializeSession
    };
};
```

### 2. 上下文感知聊天组件

```jsx
// components/ContextAwareChat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useSessionManager } from '../hooks/useSessionManager';

const ContextAwareChat = ({ userId, currentEmotion }) => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const audioRef = useRef(null);

    const {
        sessionId,
        sessionContext,
        sendContextAwareMessage,
        getConversationHistory
    } = useSessionManager(userId);

    // 加载历史对话
    useEffect(() => {
        const loadHistory = async () => {
            if (sessionId) {
                const history = await getConversationHistory(20);
                setMessages(history.map(msg => ({
                    id: `${msg.role}_${msg.timestamp}`,
                    type: msg.role === 'user' ? 'user' : 'ai',
                    content: msg.content,
                    timestamp: new Date(msg.timestamp * 1000),
                    emotion: msg.emotion
                })));
            }
        };

        loadHistory();
    }, [sessionId, getConversationHistory]);

    // 发送消息
    const handleSendMessage = async () => {
        if (!inputText.trim() || isProcessing) return;

        const userMessage = inputText.trim();
        setInputText('');
        setIsProcessing(true);

        // 添加用户消息到UI
        const userMsg = {
            id: `user_${Date.now()}`,
            type: 'user',
            content: userMessage,
            timestamp: new Date(),
            emotion: currentEmotion
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            // 发送上下文感知消息
            const result = await sendContextAwareMessage(userMessage, currentEmotion);

            if (result) {
                // 添加AI回应到UI
                const aiMsg = {
                    id: `ai_${Date.now()}`,
                    type: 'ai',
                    content: result.ai_response,
                    timestamp: new Date(),
                    detectedEmotion: result.detected_emotion,
                    contextUsed: result.context_used,
                    audioData: result.audio_data
                };
                setMessages(prev => [...prev, aiMsg]);

                // 播放语音回应
                if (result.audio_data) {
                    playAudioResponse(result.audio_data);
                }
            }
        } catch (error) {
            console.error('❌ 发送消息失败:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    // 播放语音回应
    const playAudioResponse = (audioData) => {
        try {
            const audioBlob = new Blob([
                Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
            ], { type: 'audio/mpeg' });
            
            const audioUrl = URL.createObjectURL(audioBlob);
            audioRef.current.src = audioUrl;
            audioRef.current.play();
        } catch (error) {
            console.error('❌ 播放语音失败:', error);
        }
    };

    return (
        <div className="context-aware-chat">
            {/* 会话上下文显示 */}
            <SessionContextDisplay context={sessionContext} />
            
            {/* 消息列表 */}
            <div className="messages-container">
                {messages.map(msg => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                
                {isProcessing && (
                    <div className="typing-indicator">
                        🤖 AI正在基于对话历史思考回应...
                    </div>
                )}
            </div>
            
            {/* 输入区域 */}
            <div className="input-container">
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="继续你们的对话..."
                    disabled={isProcessing}
                />
                <button onClick={handleSendMessage} disabled={isProcessing}>
                    发送
                </button>
            </div>
            
            <audio ref={audioRef} style={{ display: 'none' }} />
        </div>
    );
};

// 会话上下文显示组件
const SessionContextDisplay = ({ context }) => {
    if (!context || Object.keys(context).length === 0) return null;

    return (
        <div className="session-context">
            <h4>📊 对话上下文</h4>
            <div className="context-stats">
                <span>💬 消息: {context.message_count}</span>
                <span>🎭 情绪: {context.emotions_detected?.join(', ')}</span>
                <span>⏱️ 时长: {Math.round(context.session_duration / 60)}分钟</span>
            </div>
            {context.context_summary && (
                <div className="context-summary">
                    <strong>📝 对话摘要:</strong> {context.context_summary}
                </div>
            )}
        </div>
    );
};

// 消息气泡组件
const MessageBubble = ({ message }) => {
    return (
        <div className={`message-bubble ${message.type}`}>
            <div className="message-content">{message.content}</div>
            
            {message.emotion && (
                <div className="message-emotion">
                    情绪: {message.emotion}
                </div>
            )}
            
            {message.contextUsed && (
                <div className="context-indicator">
                    🧠 使用了对话历史上下文
                </div>
            )}
            
            <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
            </div>
        </div>
    );
};

export default ContextAwareChat;
```

## 🔧 后端API端点

### 会话管理端点

```python
# backend/services/gateway/api/routes.py 中添加

@app.post("/api/v1/session/create")
async def create_session(request: dict):
    """创建新会话"""
    user_id = request.get("user_id")
    session_id = session_manager.create_session(user_id)
    
    return {
        "session_id": session_id,
        "status": "created"
    }

@app.get("/api/v1/session/{session_id}/context")
async def get_session_context(session_id: str):
    """获取会话上下文"""
    context = session_manager.get_session_context(session_id)
    return context

@app.get("/api/v1/session/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 10):
    """获取对话历史"""
    history = session_manager.get_conversation_history(session_id, limit)
    return [asdict(msg) for msg in history]

@app.post("/api/v1/unified/emotion_chat")
async def unified_emotion_chat(request: dict):
    """统一的情感感知对话端点 - 支持会话上下文"""
    message = request.get("message")
    user_id = request.get("user_id")
    session_id = request.get("session_id")
    emotion_context = request.get("emotion_context")
    use_session_context = request.get("use_session_context", True)
    
    # 如果启用会话上下文，传递session_id给对话引擎
    conversation_payload = {
        "message": message,
        "user_id": user_id,
        "emotion_context": emotion_context
    }
    
    if use_session_context and session_id:
        conversation_payload["session_id"] = session_id
    
    # 调用对话引擎 (会自动处理会话上下文)
    response = await call_conversation_service(conversation_payload)
    
    # 返回结果包含会话上下文信息
    result = {
        "ai_response": response["response"],
        "detected_emotion": emotion_context,
        "session_id": session_id,
        "context_used": use_session_context
    }
    
    if session_id:
        result["session_context"] = session_manager.get_session_context(session_id)
    
    return result
```

## 📱 使用示例

### 完整的对话流程

```jsx
// App.jsx
import React, { useState } from 'react';
import ContextAwareChat from './components/ContextAwareChat';
import EmotionDetector from './components/EmotionDetector';

const App = () => {
    const [currentUser] = useState('user123');
    const [currentEmotion, setCurrentEmotion] = useState('neutral');

    return (
        <div className="app">
            <h1>🎭 EmoHunter - 情感感知语音助手</h1>
            
            {/* 情绪检测组件 */}
            <EmotionDetector onEmotionChange={setCurrentEmotion} />
            
            {/* 上下文感知聊天组件 */}
            <ContextAwareChat 
                userId={currentUser}
                currentEmotion={currentEmotion}
            />
        </div>
    );
};

export default App;
```

## 🎯 关键特性

### ✅ 已实现功能

1. **自动会话管理**: 用户登录时自动创建或恢复会话
2. **上下文感知对话**: AI能记住之前的对话内容
3. **情绪历史跟踪**: 记录用户在对话中的情绪变化
4. **会话持久化**: 支持应用重启后恢复对话
5. **多用户隔离**: 每个用户的会话完全独立
6. **智能上下文摘要**: 长对话自动生成摘要避免上下文过长

### 🔄 对话流程

```
1. 用户登录 → 创建/恢复会话
2. 用户发送消息 → 检测情绪
3. 系统获取历史上下文 → 构建情感感知提示词
4. GPT-4o生成回应 → 考虑历史和情绪
5. 保存对话记录 → 更新会话上下文
6. 语音合成播放 → 完成一轮对话
```

## 💡 最佳实践

### 1. 会话生命周期管理
- 自动清理过期会话（24小时）
- 支持手动清除会话
- 会话恢复验证

### 2. 上下文优化
- 限制历史消息长度（避免token超限）
- 智能上下文摘要
- 关键信息提取

### 3. 性能优化
- 会话数据缓存
- 异步历史加载
- 增量上下文更新

你的会话存储系统现在已经完全实现！🎉 用户可以享受真正连续、上下文感知的对话体验，AI能够记住之前的对话内容并提供更加个性化和相关的回应。
