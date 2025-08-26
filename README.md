EmoHunter 🎭


Real-Time Emotion Detection & AI Voice Agent with Apple Watch Biometric Integration

A production-ready FastAPI application that combines real-time facial emotion detection, Apple Watch biometric data analysis, and intelligent voice conversations. Built for the Pond Hackathon, EmoHunter creates emotionally-aware AI interactions using computer vision, physiological data analysis, natural language processing, and voice synthesis for comprehensive mental health monitoring.


🚀 Live Deployments


✅ Multi-Platform Architecture

🎭 EmoHunter Backend: https://emohunter-biometric-api-6106408799.us-central1.run.app (Live with Apple Watch Integration)
🌐 Vault Frontend (Web): https://pond-hack-multi-sig-vault.vercel.app/
📱 Swift Frontend (iOS): Swift Frontend Repo
📜 BSC Smart Contracts: BSC Testnet - 0x3e27d1471e73BaB92D30A005218ba156Db13e76f
📜 TRON Smart Contract Feature:

Demo: https://tron-multisig-dapp.vercel.app/
Contract Address: TWy9c8h8wF8uvrYSLA2CpWeEadYU4zxUd7
Network: TRON Nile Testnet




Architecture Overview


EmoHunter Backend: Google Cloud Run deployment with emotion detection & simplified voice AI
Vault Frontend (Web): Vercel-deployed multi-sig vault
Swift Frontend (iOS): Native iOS client for biometric & emotion interaction
Smart Contracts: Deployed on BSC Testnet and TRON Testnet with incentive engine
Integration: Multi-service architecture with cross-platform communication
Voice System: Unified ElevenLabs TTS with consistent Rachel voice across all emotions



✨ Key Features



🎥 Real-Time Emotion Detection


Computer Vision: OpenCV-powered webcam integration
Emotion Analysis: Advanced facial emotion recognition with FER library
Real-Time Streaming: WebSocket and Server-Sent Events support
Stability Engine: Smart emotion persistence to prevent rapid changes
Browser Integration: Direct camera frame processing from web clients



🤖 AI-Powered Voice Agent


Emotional Intelligence: GPT-4o integration for context-aware conversations
Voice Synthesis: ElevenLabs API with unified Rachel voice (consistent across all emotions)
Session Management: Persistent conversation context and user tracking
Multi-Modal: Text and audio response generation
Simplified Configuration: Single voice settings for better maintainability



🍎 Apple Watch Biometric Integration


Multi-Condition Trigger Detection: Personalized HR/HRV/sleep analysis for anxiety detection
Personalized Baselines: Individual physiological normal values
CBT/DBT Integration: Evidence-based therapeutic interventions
Proactive Monitoring: Automatic intervention triggers
Wellness Scoring: Comprehensive health assessment (0-100 scale)
Mock Data: Realistic fallback data for testing



🔐 Trust Commit System (NEW)


Privacy-Preserving Blockchain Commitment for Emotional Health Sessions

A cryptographically secure system that anchors verifiable commitments of EmoHunter therapy sessions on the KiteAI blockchain while ensuring zero personal data is exposed. This adds accountability, transparency, and compliance to AI-powered emotional health services without compromising user privacy.

Privacy-First: Zero PII on-chain, user-specific derived keys, deterministic JSON
Cryptographic Security: Ed25519 signatures, HMAC-SHA256 hashing, HKDF key derivation
Blockchain Integration: Native KiteAI agent registration, dev/production modes, retry fallback
Commitment Flow: Session → Canonical JSON → HMAC hash → Ed25519 signature → Blockchain anchor → Local receipt
API Endpoints:

POST /trust/commit → Create session commitment
GET /trust/verify → Verify existing commitment
GET /trust/health → System & blockchain status

Compliance: GDPR & HIPAA ready, no PII/PHI stored, audit trail via blockchain
Guarantees: Integrity, authenticity, non-repudiation, privacy




🏗️ Production Architecture


Modular Design: Clean separation of services and concerns
Scalable Backend: FastAPI with async/await patterns
Cloud Native: Docker containerization with Google Cloud Run deployment
API-First: RESTful endpoints with comprehensive documentation
Real-Time Communication: WebSocket support for live interactions



🔄 Recent Improvements



Voice Configuration Simplification


Unified Voice System: Replaced emotion-based voice variations with single consistent Rachel voice
Simplified Settings: Single configuration (stability: 0.70, similarity_boost: 0.80, style: 0.50)
Better Maintainability: Reduced complexity while maintaining high-quality TTS
Consistent User Experience: Same voice quality across all emotional contexts



Deployment & Integration


Branch Integration: Successfully merged contracts and backend-dev-zou branches into main
Dependency Resolution: Fixed FastAPI/TensorFlow compatibility issues for GCP deployment
Docker Optimization: Enhanced Dockerfile with comprehensive system dependencies
Clean Codebase: Removed legacy files and consolidated documentation
Multi-Platform Ready: Aligned architecture across GCP, Vercel, iOS Swift, BSC Testnet, and TRON Testnet



Current Status


Voice System: ✅ Simplified and deployed
BSC Smart Contracts: ✅ Live on BSC Testnet
TRON Smart Contracts: ✅ Live on Nile Testnet
Vault Frontend (Web): ✅ Live on Vercel
Swift Frontend (iOS): ✅ Available on GitHub
Backend Deployment: 🔄 In progress on GCP Cloud Run
Trust Commit System: ✅ Integrated with blockchain anchoring




API Endpoints



Emotion Detection


GET /current_emotion - Get the current detected emotion
GET /start_emotion_stream - Stream emotion detection results (Server-Sent Events)
GET /ws/emotions - WebSocket endpoint for real-time updates
POST /analyze_frame - Process camera frames from browser



Voice Agent


POST /talk - Generate speech based on text and emotion

{
  "text": "You seem tense. Would you like to take a break?",
  "emotion": "angry"
}



Utility


GET / - API welcome message
GET /emotions/available - List available emotions and voice mappings
GET /health - System status and camera info



🍎 Apple Watch Biometric Integration


POST /api/v1/biometric/upload - Upload Apple Watch biometric data
POST /api/v1/biometric/mock/{user_id} - Generate mock biometric data
GET /api/v1/biometric/context/{user_id} - Get biometric emotional context
GET /api/v1/biometric/triggers/{user_id} - Get biometric triggers and alerts
POST /api/v1/biometric/proactive_intervention/{user_id} - Trigger proactive interventions
GET /integrated_analysis/{user_id} - Combined facial emotion + biometric analysis




Setup



1. Setup Environment

uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

2. Configure Environment

cp .env.example .env
# Add your API keys:
# ELEVENLABS_API_KEY=your_elevenlabs_key
# OPENAI_API_KEY=your_openai_key

3. Run Modular Backend

cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

4. Testing

python test_modular_architecture.py



Emotion to Voice Mapping

Emotion
ElevenLabs Voice
Characteristics
Happy
Rachel
Bright, cheerful
Sad
Bella
Soft, gentle
Angry
Josh
Strong, assertive
Fear
Elli
Cautious, gentle
Surprise
Antoni
Energetic, expressive
Disgust
Arnold
Neutral, controlled
Neutral
Sam
Balanced, natural



Testing



🎥 Camera Emotion Detection

python main.py
open camera_test_ui.html

🧪 Comprehensive Testing

python test_client.py

🌐 Interactive Web Testing


Camera Test UI (camera_test_ui.html)
Full Test UI (test_ui.html)
WebSocket Test (websocket_test.html)




🎯 Project Status



✅ Production Ready


Cloud Deployment on Google Cloud Run
Modular Architecture with service separation
Real-time facial emotion detection with stability algorithms
ElevenLabs integration with emotion-mapped voices
GPT-4o powered intelligent responses
Web frontend and iOS frontend for cross-platform support
WebSocket and SSE live updates
Blockchain integration with BSC & TRON contracts
Trust Commit System for privacy-preserving commitments



🏆 Achievements


Full cloud deployment on GCP
Swift frontend client integrated
Multi-chain smart contracts (BSC + TRON)
Zero-PII blockchain trust system




🛠️ Tech Stack


Backend: FastAPI, OpenCV, FER, Pydantic, Uvicorn
AI/ML: OpenAI GPT-4o, TensorFlow, NumPy
Voice: ElevenLabs TTS API
Real-Time: WebSockets, SSE, CORS
Cloud: Google Cloud Run, Docker, GCR
Frontend: HTML5/JS Web, Swift iOS
Blockchain: BSC Testnet, TRON Nile Testnet, KiteAI Trust Commit
