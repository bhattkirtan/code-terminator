#!/bin/bash

# Test individual service locally

SERVICE=$1
PORT=$2

if [ -z "$SERVICE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./test_single.sh <service-name> <port>"
    echo "Example: ./test_single.sh upload-service 8080"
    exit 1
fi

echo "🧪 Testing $SERVICE locally on port $PORT..."

cd functions/$SERVICE

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables for local testing
export GOOGLE_CLOUD_PROJECT="test-project"
export OPENAI_API_KEY="your-openai-key-here"

# Get the function name (replace hyphens with underscores)
FUNCTION_NAME=$(echo $SERVICE | sed 's/-/_/g')

echo "🚀 Starting $SERVICE..."
echo "   Function: $FUNCTION_NAME"
echo "   Port: $PORT"
echo "   URL: http://localhost:$PORT"
echo ""
echo "💡 Tips:"
echo "   - Use Ctrl+C to stop"
echo "   - Test with: curl -X POST http://localhost:$PORT"
echo "   - Or run: python ../../test_client.py"
echo ""

# Start the function
functions-framework --target=$FUNCTION_NAME --port=$PORT --debug
