#!/bin/bash

# AI DevOps Agent Platform Startup Script

echo "🚀 Starting AI DevOps Agent Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before continuing"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p logs uploads output data temp

# Start backend
echo "🔙 Starting FastAPI backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🖥️ Starting Streamlit frontend..."
cd frontend
streamlit run main.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!
cd ..

echo "✅ AI DevOps Agent Platform started successfully!"
echo "🔗 Frontend: http://localhost:8501"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait