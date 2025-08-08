#!/bin/bash

# Deploy all cloud functions
echo "🚀 Deploying Snapit Cloud Functions..."

# Upload Service
echo "📤 Deploying Upload Service..."
gcloud functions deploy upload-service \
  --runtime python39 \
  --trigger http \
  --source ./functions/upload-service \
  --entry-point upload_file \
  --memory 512MB \
  --timeout 60s \
  --allow-unauthenticated

# Embedding Service
echo "🧠 Deploying Embedding Service..."
gcloud functions deploy embedding-service \
  --runtime python39 \
  --trigger http \
  --source ./functions/embedding-service \
  --entry-point generate_embeddings \
  --memory 1GB \
  --timeout 300s \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY

# Data Service
echo "💾 Deploying Data Service..."
gcloud functions deploy data-service \
  --runtime python39 \
  --trigger http \
  --source ./functions/data-service \
  --entry-point data_service \
  --memory 256MB \
  --timeout 30s \
  --allow-unauthenticated

# Search Service
echo "🔍 Deploying Search Service..."
gcloud functions deploy search-service \
  --runtime python39 \
  --trigger http \
  --source ./functions/search-service \
  --entry-point semantic_search \
  --memory 512MB \
  --timeout 60s \
  --allow-unauthenticated

echo "✅ All services deployed successfully!"
echo "📋 Function URLs:"
echo "   Upload: https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/upload-service"
echo "   Embedding: https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/embedding-service"
echo "   Data: https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/data-service"
echo "   Search: https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/search-service"
