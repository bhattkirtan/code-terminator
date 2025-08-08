#!/bin/bash

# Deploy Search Service to Google Cloud Functions
# Run from the search-service directory

set -e

echo "🔍 Deploying Search Service..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="search-service"

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
    --entry-point semantic_search \
    --source . \
    --timeout 60s \
    --memory 1Gi \
    --region $REGION \
    --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Search Service deployed successfully!"
    
    # Get the function URL
    FUNCTION_URL=$(gcloud functions describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(httpsTrigger.url)")
    
    echo "🌐 Function URL: $FUNCTION_URL"
    echo ""
    echo "📝 Test the service:"
    echo "curl -X POST \"$FUNCTION_URL/search\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"projectId\": \"test-project\", \"embedding\": [0.1, 0.2, 0.3], \"threshold\": 0.7}'"
    echo ""
    echo "🔍 Monitor logs:"
    echo "gcloud functions logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
    
else
    echo "❌ Deployment failed!"
    exit 1
fi
