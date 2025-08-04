#!/usr/bin/env python3
"""
💾 Session Storage System Test Demo
Session Storage System Demo - Demonstrates how to implement context-aware conversations
"""

import sys
import os
import time
import json
from datetime import datetime

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from common.services.session_manager import session_manager, StorageBackend
from common.schemas.conversation import ConversationMessage

class SessionStorageDemo:
    """Session storage system demonstration"""
    
    def __init__(self):
        self.user_id = "demo_user"
        self.session_id = None
        
    def demo_conversation_flow(self):
        """Demonstrate complete conversation flow and session storage"""
        print("💾 Session Storage System Demo")
        print("=" * 60)
        
        # 1. Create new session
        print("\n🆕 Step 1: Create new session")
        self.session_id = session_manager.create_session(self.user_id)
        print(f"✅ Session created: {self.session_id}")
        
        # 2. Simulate multi-turn conversation
        print("\n💬 Step 2: Simulate multi-turn conversation")
        
        conversations = [
            {
                "user": "Hello, I'm feeling very anxious today",
                "emotion": "fear",
                "ai": "I can sense your anxiety, and it really doesn't feel good. Would you like to tell me what's making you feel anxious?"
            },
            {
                "user": "I have an important interview tomorrow, and I'm very worried",
                "emotion": "fear", 
                "ai": "Interviews can indeed make people nervous, which is a very normal reaction. What preparations have you made for this interview?"
            },
            {
                "user": "I've prepared my resume and answers to some common questions",
                "emotion": "neutral",
                "ai": "It sounds like you've made great preparations! Being well-prepared is the best way to ease interview anxiety. Do you think there are any areas that need strengthening?"
            },
            {
                "user": "I'm worried they'll ask me questions I haven't prepared for",
                "emotion": "fear",
                "ai": "I understand your concern. Remember, interviewers also want you to succeed - they ask questions to get to know you. Even if you encounter unprepared questions, answering honestly and showing your thought process is also very good."
            },
            {
                "user": "Thank you, I feel much better now",
                "emotion": "happy",
                "ai": "I'm so glad I could help you! Seeing you shift from anxiety to a more positive state is really wonderful. Remember, you're already well-prepared, believe in yourself!"
            }
        ]
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n--- Conversation Round {i} ---")
            
            # Add user message
            user_msg = ConversationMessage(
                role="user",
                content=conv["user"],
                timestamp=time.time()
            )
            session_manager.add_message(self.session_id, user_msg, conv["emotion"])
            print(f"👤 User ({conv['emotion']}): {conv['user']}")
            
            # Add AI response
            ai_msg = ConversationMessage(
                role="assistant",
                content=conv["ai"],
                timestamp=time.time()
            )
            session_manager.add_message(self.session_id, ai_msg)
            print(f" AI: {conv['ai']}")
            
            time.sleep(0.5)  # Simulate conversation interval
        
        # 3. Show session context
        print("\n Step 3: View session context")
        context = session_manager.get_session_context(self.session_id)
        print("Session statistics:")
        print(f"  - Total messages: {context['message_count']}")
        print(f"  - Detected emotions: {', '.join(context['emotions_detected'])}")
        print(f"  - Session duration: {context['session_duration']:.1f} seconds")
        print(f"  - Last activity: {context['last_activity']}")
        
        # 4. Get conversation history
        print("\n📜 Step 4: Get conversation history")
        history = session_manager.get_conversation_history(self.session_id)
        print(f"History contains {len(history)} messages:")
        for msg in history[-4:]:  # Show last 4 messages
            role_emoji = "👤" if msg.role == "user" else "🤖"
            print(f"  {role_emoji} {msg.content[:50]}...")
        
        # 5. Demonstrate context-aware response
        print("\n🧠 Step 5: Demonstrate context-aware response")
        self.demo_context_aware_response()
        
        # 6. Demonstrate session recovery
        print("\n🔄 Step 6: Demonstrate session recovery")
        self.demo_session_recovery()
    
    def demo_context_aware_response(self):
        """Demonstrate context-aware response generation"""
        print("Testing context-aware response...")
        
        # Simulate user asking questions related to previous conversation
        new_user_message = "About that interview, what else do you think I need to prepare?"
        
        print(f"👤 User new message: {new_user_message}")
        
        # Get historical context
        history = session_manager.get_conversation_history(self.session_id)
        
        # Build context-aware prompt
        context_prompt = self.build_context_aware_prompt(new_user_message, history)
        
        print("🧠 AI analyzes context:")
        print("  - Found user previously mentioned interview anxiety")
        print("  - User emotion shifted from anxiety to positive")
        print("  - Already discussed preparations: resume, common questions")
        print("  - User's concern: unprepared questions")
        
        # Simulate AI's context-aware response
        context_aware_response = """Based on our previous conversation, I remember you've already prepared your resume and answers to common questions, which is great!
        
Considering your concern about encountering unprepared questions, I suggest you can:
1. Practice using the STAR method (Situation-Task-Action-Result) to answer behavioral questions
2. Prepare a few questions about the company and position to ask the interviewer
3. Think of specific examples of your strengths and growth experiences

Remember, you just said you feel much better - maintain this positive mindset! You're already very well prepared."""
        
        print(f"🤖 Context-aware response: {context_aware_response}")
        
        # Save this round of conversation
        user_msg = ConversationMessage(
            role="user",
            content=new_user_message,
            timestamp=time.time()
        )
        session_manager.add_message(self.session_id, user_msg, "neutral")
        
        ai_msg = ConversationMessage(
            role="assistant",
            content=context_aware_response,
            timestamp=time.time()
        )
        session_manager.add_message(self.session_id, ai_msg)
    
    def build_context_aware_prompt(self, user_message: str, history: list) -> str:
        """Build context-aware prompt"""
        # Extract key context information
        context_info = []
        
        for msg in history:
            if "interview" in msg.content.lower():
                context_info.append("User has interview-related anxiety")
            if "anxious" in msg.content.lower() or "worried" in msg.content.lower():
                context_info.append("User expressed worried emotions")
            if "prepared" in msg.content.lower() or "prepare" in msg.content.lower():
                context_info.append("Discussed interview preparation work")
        
        context_summary = "Context: " + "; ".join(set(context_info))
        
        return f"""
{context_summary}

Historical conversation key points:
- User has important interview tomorrow, feeling anxious
- Already prepared resume and common question answers
- Worried about encountering unprepared questions
- Emotions improved after communication

Current user question: {user_message}

Please provide targeted advice based on conversation history.
"""
    
    def demo_session_recovery(self):
        """Demonstrate session recovery functionality"""
        print("Testing session recovery...")
        
        # Simulate application restart or user reconnection
        original_session_id = self.session_id
        
        # Recover session through session_id
        recovered_history = session_manager.get_conversation_history(original_session_id)
        recovered_context = session_manager.get_session_context(original_session_id)
        
        print(f"✅ Successfully recovered session: {original_session_id}")
        print(f"  - Recovered {len(recovered_history)} historical messages")
        print(f"  - Recovered emotion history: {recovered_context['emotions_detected']}")
        
        # User can continue previous conversation
        continuation_message = "I just thought of something, what if I get nervous during the interview?"
        
        print(f"👤 User continues conversation: {continuation_message}")
        
        # AI can respond based on recovered context
        contextual_response = """I remember we just talked about your interview anxiety. If you feel nervous during the interview, here are some tips:

1. Deep breathing: Take a few deep breaths before the interview, this can help you relax
2. Positive self-talk: Remind yourself "I'm well prepared, I can do this"
3. Turn nervousness into excitement: Tell yourself this is a great opportunity to showcase your abilities
4. Remember interviewers are people too: They want to find the right candidate, not make things difficult for you

Based on our previous conversation, you've already made great preparations, believe in yourself!"""
        
        print(f"🤖 Response based on historical context: {contextual_response}")
    
    def demo_multiple_users(self):
        """Demonstrate multi-user session management"""
        print("\n👥 Demonstrate multi-user session management")
        print("-" * 40)
        
        # Create sessions for multiple users
        users = ["alice", "bob", "charlie"]
        sessions = {}
        
        for user in users:
            session_id = session_manager.create_session(user)
            sessions[user] = session_id
            
            # Each user sends different messages
            messages = {
                "alice": ("I'm very happy today!", "happy"),
                "bob": ("Work pressure is so high...", "sad"), 
                "charlie": ("I have to give a speech tomorrow, so nervous", "fear")
            }
            
            user_msg = ConversationMessage(
                role="user",
                content=messages[user][0],
                timestamp=time.time()
            )
            session_manager.add_message(session_id, user_msg, messages[user][1])
            
            print(f"👤 {user}: {messages[user][0]} ({messages[user][1]})")
        
        print(f"\n📈 Current active sessions: {session_manager.get_active_sessions_count()}")
        
        # Show each user's session context
        for user, session_id in sessions.items():
            context = session_manager.get_session_context(session_id)
            print(f"  {user}: {context['emotions_detected']} - {context['message_count']} messages")

if __name__ == "__main__":
    print("🚀 EmoHunter Session Storage System Demo")
    print("Demonstrates how to implement context-aware voice assistant conversations")
    print("=" * 60)
    
    demo = SessionStorageDemo()
    
    try:
        # Main demonstration
        demo.demo_conversation_flow()
        
        # Multi-user demonstration
        demo.demo_multiple_users()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed!")
        print("\n💡 Key features:")
        print("✅ Automatic session creation and management")
        print("✅ Conversation history storage and retrieval") 
        print("✅ Emotion context tracking")
        print("✅ Context-aware response generation")
        print("✅ Session recovery functionality")
        print("✅ Multi-user session isolation")
        
        print("\n🔧 Integration methods in UI:")
        print("1. Create or recover session when user logs in")
        print("2. Pass session_id with each conversation")
        print("3. AI automatically retrieves historical context")
        print("4. Generate context-aware responses")
        print("5. Automatically save conversation records")
        
    except Exception as e:
        print(f"❌ Error occurred during demonstration: {e}")
        import traceback
        traceback.print_exc()
