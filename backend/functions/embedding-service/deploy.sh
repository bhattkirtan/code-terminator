#!/bin/bash

# Deploy Embedding Service to Google Cloud Functions
# Run from the embedding-service directory

set -e

echo "🧠 Deploying AI Embedding Service..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="embedding-service"

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION" 
echo "   Service Name: $SERVICE_NAME"

# Confirm deployment
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo "🚀 Deploying function..."

# Deploy the function
gcloud functions deploy $SERVICE_NAME \
    --gen2 \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point embedding_service \
    --source . \
    --timeout 540s \
    --memory 2Gi \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY"

if [ $? -eq 0 ]; then
    echo "✅ Embedding Service deployed successfully!"
    
    # Get the function URL
    FUNCTION_URL=$(gcloud functions describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(httpsTrigger.url)")
    
    echo "🌐 Function URL: $FUNCTION_URL"
    echo ""
    echo "📝 Test the service:"
    echo "curl -X POST \"$FUNCTION_URL/api/analyze_image\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"projectId\": \"test-project\", \"imageId\": \"img123\"}'"
    echo ""
    echo "🔍 Monitor logs:"
    echo "gcloud functions logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
    
else
    echo "❌ Deployment failed!"
    exit 1
fi
