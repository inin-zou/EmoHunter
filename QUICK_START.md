# EmoHunter Quick Start Guide

## Current Setup
- ✅ **Frontend**: Deployed on Vercel
- ✅ **Smart Contracts**: Deployed on testnet  
- ✅ **Backend**: Local development ready

## Local Development

### 1. Start the Main Application
```bash
python simple_test_launcher.py
```
This starts the main EmoHunter FastAPI server with emotion detection and voice interaction.

### 2. Access Your Deployed Services
- **Frontend**: Available on Vercel
- **Smart Contracts**: Deployed on testnet
- **Integration**: Frontend connects directly to contracts

## Key Features Available

### Main Application (`simple_test_launcher.py`)
- 🎥 Real-time emotion detection via webcam
- 🎤 Voice interaction with ElevenLabs
- 🤖 AI conversations with OpenAI GPT-4o
- 📊 Session management and emotion tracking

### Incentive Engine (`mock_service.py`)
- 🏆 Reward calculation based on emotions
- 📈 Multi-tier reward system (Bronze/Silver/Gold/Platinum)
- 👤 User statistics and session tracking
- 🔗 API endpoints for integration

## Environment Configuration

All configuration is in the root `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `DEV_MODE=true`: Development mode enabled
- `MOCK_BLOCKCHAIN=true`: Use mock blockchain locally

## Integration with Deployed Services

Your local backend can integrate with:
- **Vercel Frontend**: Already deployed and accessible
- **Testnet Contracts**: Already deployed and functional
- **Local Services**: For development and testing

## Next Steps

1. **Test locally**: Run `python simple_test_launcher.py`
2. **Verify emotion detection**: Use the web UI at `http://localhost:8000`
3. **Test voice interaction**: Speak to the system
4. **Check incentive engine**: Run mock service and tests

## Troubleshooting

- **Camera not working**: Check `CAMERA_INDEX` in `.env`
- **Voice not working**: Verify `ELEVENLABS_API_KEY` in `.env`
- **AI not responding**: Check `OPENAI_API_KEY` in `.env`
- **Port conflicts**: Adjust ports in `.env` file

Your EmoHunter system is ready for local development! 🚀
