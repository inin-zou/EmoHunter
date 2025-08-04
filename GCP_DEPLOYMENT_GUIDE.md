# 🎭 EmoHunter GCP Deployment Guide

This guide will help you deploy your EmoHunter FastAPI application to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Ensure you have a Google Cloud account with billing enabled
2. **Google Cloud SDK**: Install the gcloud CLI tool
3. **Docker**: Install Docker on your local machine
4. **API Keys**: Have your ElevenLabs and OpenAI API keys ready

## Quick Deployment Steps

### 1. Setup Google Cloud Project

```bash
# Install Google Cloud SDK if not already installed
# Visit: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create emohunter-project --name="EmoHunter"

# Set the project
gcloud config set project emohunter-project

# Enable billing for the project (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing
```

### 2. Run the Deployment Script

```bash
# Make sure you're in the project directory
cd /path/to/EmoHunter-Pond_Hackathon

# Run the deployment script
./deploy.sh
```

The script will:
- Enable required Google Cloud APIs
- Build your Docker image
- Push it to Google Container Registry
- Deploy to Cloud Run
- Provide you with the service URL

### 3. Set Environment Variables

After deployment, set your API keys:

```bash
gcloud run services update emohunter-api \
    --region=us-central1 \
    --set-env-vars ELEVENLABS_API_KEY=your_elevenlabs_key,OPENAI_API_KEY=your_openai_key
```

### 4. Test Your Deployment

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe emohunter-api --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/health

# Test main endpoint
curl $SERVICE_URL/
```

## Manual Deployment (Alternative)

If you prefer manual deployment:

### 1. Build and Push Docker Image

```bash
# Set your project ID
PROJECT_ID=your-project-id

# Build the image
docker build -t gcr.io/$PROJECT_ID/emohunter-api .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/emohunter-api
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy emohunter-api \
    --image gcr.io/$PROJECT_ID/emohunter-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10
```

## Configuration Details

### Resource Allocation
- **Memory**: 2GB (required for OpenCV and TensorFlow)
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds
- **Concurrency**: 80 requests per instance
- **Max Instances**: 10

### Environment Variables
- `PORT`: 8080 (automatically set by Cloud Run)
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `OPENAI_API_KEY`: Your OpenAI API key

## API Endpoints

Once deployed, your API will be available at:
- `GET /` - Service info
- `GET /health` - Health check
- `POST /analyze_emotion` - Image emotion analysis
- `GET /current_emotion` - Current emotion detection
- `POST /api/v1/voice_conversation` - Voice conversation
- `POST /generate` - Text conversation
- And more...

## Monitoring and Logs

View logs and monitor your service:

```bash
# View logs
gcloud logs read --service=emohunter-api --limit=50

# Monitor in Cloud Console
# Visit: https://console.cloud.google.com/run
```

## Troubleshooting

### Common Issues

1. **Build Failures**: Check Docker build locally first
2. **Memory Issues**: Increase memory allocation if needed
3. **Timeout Issues**: Increase timeout for heavy ML operations
4. **API Key Issues**: Ensure environment variables are set correctly

### Debug Commands

```bash
# Check service status
gcloud run services describe emohunter-api --region=us-central1

# View recent logs
gcloud logs read --service=emohunter-api --limit=20

# Update service configuration
gcloud run services update emohunter-api --region=us-central1 --memory=4Gi
```

## Cost Optimization

- Cloud Run charges only for actual usage
- Consider setting max instances based on expected traffic
- Monitor usage in Cloud Console billing section

## Security Considerations

- API keys are stored as environment variables
- Service allows unauthenticated access (suitable for demo/testing)
- For production, consider implementing authentication

---

🎉 **Your EmoHunter API is now ready for the cloud!**
