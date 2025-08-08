#!/bin/bash

# Master deployment script for all AI DevOps Agent Platform services
# Run from the backend/functions directory

set -e

echo "🚀 AI DevOps Agent Platform - Master Deployment"
echo "=================================================="

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}

if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Please provide your Google Cloud Project ID:"
    echo "Usage: ./deploy-all.sh YOUR_PROJECT_ID [REGION]"
    exit 1
fi

echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Services: 6 total"

# Confirm deployment
read -p "Deploy all services to Google Cloud Functions? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY environment variable not set."
    echo "Services requiring OpenAI will need this to function properly."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please set OPENAI_API_KEY and try again."
        exit 1
    fi
fi

echo ""
echo "🚀 Starting deployment of all services..."
echo ""

# Service deployment order (dependencies first)
services=(
    "project-init-service:🏗️"
    "data-service:💾"
    "upload-service:📤"
    "embedding-service:🧠"
    "search-service:🔍"
    "link-service:🔗"
)

success_count=0
failed_services=()

for service_info in "${services[@]}"; do
    IFS=':' read -r service_name service_icon <<< "$service_info"
    
    echo "----------------------------------------"
    echo "$service_icon Deploying $service_name..."
    echo "----------------------------------------"
    
    if [ -d "$service_name" ]; then
        cd "$service_name"
        
        if [ -f "./deploy.sh" ]; then
            # Run the individual deployment script
            if ./deploy.sh "$PROJECT_ID" "$REGION"; then
                echo "✅ $service_name deployed successfully!"
                ((success_count++))
            else
                echo "❌ $service_name deployment failed!"
                failed_services+=("$service_name")
            fi
        else
            echo "❌ Deploy script not found for $service_name"
            failed_services+=("$service_name")
        fi
        
        cd ..
    else
        echo "❌ Service directory not found: $service_name"
        failed_services+=("$service_name")
    fi
    
    echo ""
done

echo "=================================================="
echo "🎉 Deployment Summary"
echo "=================================================="
echo "Total Services: ${#services[@]}"
echo "Successfully Deployed: $success_count"
echo "Failed: ${#failed_services[@]}"

if [ ${#failed_services[@]} -eq 0 ]; then
    echo ""
    echo "🎊 ALL SERVICES DEPLOYED SUCCESSFULLY! 🎊"
    echo ""
    echo "📋 Service URLs (check individual deployment logs above for exact URLs):"
    echo "   🏗️ Project Init: https://$REGION-$PROJECT_ID.cloudfunctions.net/project-init-service"
    echo "   💾 Data Service: https://$REGION-$PROJECT_ID.cloudfunctions.net/data-service"
    echo "   📤 Upload Service: https://$REGION-$PROJECT_ID.cloudfunctions.net/upload-service"
    echo "   🧠 Embedding Service: https://$REGION-$PROJECT_ID.cloudfunctions.net/embedding-service"
    echo "   🔍 Search Service: https://$REGION-$PROJECT_ID.cloudfunctions.net/search-service"
    echo "   🔗 Link Service: https://$REGION-$PROJECT_ID.cloudfunctions.net/link-service"
    echo ""
    echo "🚀 Your AI DevOps Agent Platform backend is ready!"
    echo ""
    echo "Next Steps:"
    echo "1. Test the services using the provided curl commands"
    echo "2. Configure your frontend to use these endpoints"
    echo "3. Set up monitoring and alerting"
    echo "4. Configure custom domains if needed"
else
    echo ""
    echo "❌ Some services failed to deploy:"
    for failed_service in "${failed_services[@]}"; do
        echo "   - $failed_service"
    done
    echo ""
    echo "Please check the error messages above and retry deployment for failed services."
fi

echo ""
echo "📊 Monitor all services:"
echo "gcloud functions list --project=$PROJECT_ID --region=$REGION"
echo ""
echo "📝 View logs:"
echo "gcloud functions logs read [SERVICE-NAME] --project=$PROJECT_ID --region=$REGION"
