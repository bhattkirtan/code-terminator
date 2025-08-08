#!/bin/bash

# Deploy Upload Service to Google Cloud Functions
# Run from the upload-service directory

set -e

echo "📤 Deploying Upload Service..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="upload-service"

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
    --entry-point upload_file \
    --source . \
    --timeout 60s \
    --memory 512Mi \
    --region $REGION \
    --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Upload Service deployed successfully!"
    
    # Get the function URL
    FUNCTION_URL=$(gcloud functions describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(httpsTrigger.url)")
    
    echo "🌐 Function URL: $FUNCTION_URL"
    echo ""
    echo "📝 Test the service:"
    echo "curl -X POST \"$FUNCTION_URL/api/upload\" \\"
    echo "  -F \"files=@test-image.png\" \\"
    echo "  -F \"projectId=test-project\" \\"
    echo "  -F \"fileType=ui-image\""
    echo ""
    echo "🔍 Monitor logs:"
    echo "gcloud functions logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
    
else
    echo "❌ Deployment failed!"
    exit 1
fi
