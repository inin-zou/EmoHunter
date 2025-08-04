# 🎭🤖 UI集成指南：情感感知对话系统

## 📋 完整工作流程实现

### 🎯 你描述的工作流程：
```
用户输入（语音或文本）
     ↓
Emotion Analysis Engine 获取当前面部情绪（如 sad, angry）
     ↓
将文本 + 情绪上下文组合为 Prompt，发给 Conversation Engine
     ↓
Conversation Engine 用 GPT-4o 生成回应（带情感调性）
     ↓
ElevenLabs 语音合成，参考 emotion 调整语气
     ↓
UI 播放最终语音回复
```

## 🚀 API端点使用

### 方法1: 统一API（推荐）
```javascript
// 一次调用完成整个流程
async function sendEmotionAwareMessage(userMessage) {
    const response = await fetch('http://localhost:8000/api/v1/unified/emotion_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: userMessage,
            user_id: 'current_user',
            include_emotion: true,
            include_voice: true
        })
    });
    
    const result = await response.json();
    
    // 结果包含：
    // - detected_emotion: 检测到的情绪
    // - ai_response: GPT-4o生成的情感感知回应
    // - audio_data: ElevenLabs合成的语音（base64编码）
    // - emotion_context: 使用的情感上下文
    
    return result;
}
```

### 方法2: 分步调用（更灵活）
```javascript
// 步骤1: 获取当前情绪
async function getCurrentEmotion() {
    const response = await fetch('http://localhost:8001/current_emotion');
    return await response.json();
}

// 步骤2: 生成情感感知回应
async function generateEmotionAwareResponse(message, emotion) {
    const emotionPrompt = createEmotionPrompt(message, emotion);
    
    const response = await fetch('http://localhost:8002/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: emotionPrompt,
            user_id: 'current_user',
            emotion_context: emotion
        })
    });
    
    return await response.json();
}

// 步骤3: 语音合成
async function synthesizeEmotionVoice(text, emotion) {
    const response = await fetch('http://localhost:8002/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            emotion: emotion,
            voice: 'Rachel'
        })
    });
    
    return await response.json();
}

// 创建情感感知提示词
function createEmotionPrompt(userMessage, emotionData) {
    const emotionContexts = {
        "happy": "用户看起来很开心。请用温暖、友好的语调回应。",
        "sad": "用户看起来难过。请用温柔、理解的语调回应，提供安慰。",
        "angry": "用户看起来愤怒。请用冷静、耐心的语调回应。",
        "fear": "用户看起来担心。请用安抚、鼓励的语调回应。",
        "surprise": "用户看起来惊讶。请用好奇、兴奋的语调回应。",
        "disgust": "用户看起来不满。请用理解、同情的语调回应。",
        "neutral": "用户表情平静。请用自然、友好的语调回应。"
    };
    
    const context = emotionContexts[emotionData.emotion] || emotionContexts.neutral;
    
    return `
情感上下文: ${context}
当前用户情绪: ${emotionData.emotion} (置信度: ${emotionData.confidence})

用户消息: ${userMessage}

请根据用户情绪用合适的语调回应。
`;
}
```

## 🎨 前端UI实现示例

### React组件示例
```jsx
import React, { useState, useRef, useEffect } from 'react';

const EmotionAwareChat = () => {
    const [messages, setMessages] = useState([]);
    const [currentEmotion, setCurrentEmotion] = useState('neutral');
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const audioRef = useRef(null);

    // 实时情绪检测
    useEffect(() => {
        const emotionInterval = setInterval(async () => {
            try {
                const emotion = await getCurrentEmotion();
                setCurrentEmotion(emotion.emotion);
            } catch (error) {
                console.log('情绪检测失败，使用默认值');
            }
        }, 2000); // 每2秒更新一次情绪

        return () => clearInterval(emotionInterval);
    }, []);

    // 发送消息并获取情感感知回应
    const handleSendMessage = async (userMessage) => {
        setIsProcessing(true);
        
        // 添加用户消息到聊天记录
        const userMsg = {
            type: 'user',
            content: userMessage,
            emotion: currentEmotion,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            // 调用统一API获取情感感知回应
            const result = await sendEmotionAwareMessage(userMessage);
            
            // 添加AI回应到聊天记录
            const aiMsg = {
                type: 'ai',
                content: result.ai_response,
                detectedEmotion: result.detected_emotion,
                audioData: result.audio_data,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMsg]);
            
            // 播放语音回应
            if (result.audio_data) {
                playAudioResponse(result.audio_data);
            }
            
        } catch (error) {
            console.error('发送消息失败:', error);
            // 添加错误消息
            setMessages(prev => [...prev, {
                type: 'error',
                content: '抱歉，我现在无法回应。请稍后再试。',
                timestamp: new Date()
            }]);
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
            console.error('播放语音失败:', error);
        }
    };

    // 情绪显示组件
    const EmotionIndicator = ({ emotion }) => {
        const emotionEmojis = {
            happy: '😊', sad: '😢', angry: '😠',
            fear: '😰', surprise: '😲', disgust: '🤢',
            neutral: '😐'
        };
        
        return (
            <div className="emotion-indicator">
                <span className="emotion-emoji">{emotionEmojis[emotion]}</span>
                <span className="emotion-text">当前情绪: {emotion}</span>
            </div>
        );
    };

    return (
        <div className="emotion-chat-container">
            {/* 情绪指示器 */}
            <EmotionIndicator emotion={currentEmotion} />
            
            {/* 聊天消息区域 */}
            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.type}`}>
                        <div className="message-content">{msg.content}</div>
                        {msg.detectedEmotion && (
                            <div className="detected-emotion">
                                检测情绪: {msg.detectedEmotion}
                            </div>
                        )}
                        <div className="timestamp">
                            {msg.timestamp.toLocaleTimeString()}
                        </div>
                    </div>
                ))}
                
                {isProcessing && (
                    <div className="message ai processing">
                        <div className="typing-indicator">AI正在思考中...</div>
                    </div>
                )}
            </div>
            
            {/* 输入区域 */}
            <ChatInput 
                onSendMessage={handleSendMessage}
                disabled={isProcessing}
            />
            
            {/* 隐藏的音频播放器 */}
            <audio ref={audioRef} style={{ display: 'none' }} />
        </div>
    );
};

// 聊天输入组件
const ChatInput = ({ onSendMessage, disabled }) => {
    const [inputText, setInputText] = useState('');
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (inputText.trim() && !disabled) {
            onSendMessage(inputText.trim());
            setInputText('');
        }
    };
    
    return (
        <form onSubmit={handleSubmit} className="chat-input-form">
            <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="输入你的消息..."
                disabled={disabled}
                className="chat-input"
            />
            <button 
                type="submit" 
                disabled={disabled || !inputText.trim()}
                className="send-button"
            >
                发送
            </button>
        </form>
    );
};

export default EmotionAwareChat;
```

## 🎨 CSS样式示例
```css
.emotion-chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
}

.emotion-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f0f8ff;
    border-radius: 10px;
    margin-bottom: 20px;
}

.emotion-emoji {
    font-size: 24px;
}

.emotion-text {
    font-weight: bold;
    color: #2c3e50;
}

.messages-container {
    height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    background: white;
}

.message {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 10px;
    max-width: 70%;
}

.message.user {
    background: #007bff;
    color: white;
    margin-left: auto;
    text-align: right;
}

.message.ai {
    background: #f8f9fa;
    color: #333;
    border: 1px solid #dee2e6;
}

.message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.detected-emotion {
    font-size: 12px;
    color: #6c757d;
    margin-top: 5px;
    font-style: italic;
}

.timestamp {
    font-size: 11px;
    color: #6c757d;
    margin-top: 5px;
}

.typing-indicator {
    color: #6c757d;
    font-style: italic;
}

.chat-input-form {
    display: flex;
    gap: 10px;
}

.chat-input {
    flex: 1;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 14px;
}

.chat-input:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.send-button {
    padding: 12px 24px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
}

.send-button:hover:not(:disabled) {
    background: #0056b3;
}

.send-button:disabled {
    background: #6c757d;
    cursor: not-allowed;
}
```

## 🚀 启动服务进行测试

```bash
# 1. 启动所有服务
cd backend
docker-compose up --build

# 或者分别启动各个服务：
# 终端1: 情绪分析引擎
cd backend/services/emotion_analysis_engine
python main.py

# 终端2: 对话引擎  
cd backend/services/conversation_engine
python main.py

# 终端3: API网关
cd backend/services/gateway
python main.py

# 2. 测试完整工作流程
python test_emotion_conversation_flow.py
```

## 🎯 关键特性

### ✅ 已实现功能
1. **实时情绪检测**: 每2秒更新用户面部情绪
2. **情感上下文注入**: 自动将情绪信息添加到GPT提示词
3. **情感感知回应**: GPT-4o根据情绪生成合适语调的回应
4. **情感语音合成**: ElevenLabs根据情绪调整语音参数
5. **统一API接口**: 一次调用完成整个流程

### 🎨 UI集成要点
1. **实时情绪显示**: 在UI中显示当前检测到的情绪
2. **情绪历史**: 在聊天记录中显示每条消息对应的情绪
3. **语音播放**: 自动播放AI生成的情感语音回应
4. **加载状态**: 显示AI思考和语音合成进度

你的微服务架构已经完美支持了这个工作流程！现在你只需要在前端UI中调用相应的API端点就可以实现完整的情感感知对话系统了。🎭🤖✨
