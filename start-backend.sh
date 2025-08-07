#!/bin/bash

# AI DevOps Agent Platform - Backend Startup Script

echo "🚀 Starting AI DevOps Agent Platform Backend..."
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Set environment variables
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export RELOAD=${RELOAD:-true}

echo "🔧 Configuration:"
echo "   - Host: $HOST"
echo "   - Port: $PORT"
echo "   - Reload: $RELOAD"

# Start the server
echo ""
echo "🌟 Starting FastAPI server..."
echo "   - API Docs: http://localhost:$PORT/docs"
echo "   - Health Check: http://localhost:$PORT/health"
echo "   - Agent Status: http://localhost:$PORT/agents/status"
echo ""

if [ "$RELOAD" = "true" ]; then
    python3 -m uvicorn backend.main:app --reload --host $HOST --port $PORT
else
    python3 -m uvicorn backend.main:app --host $HOST --port $PORT
fi