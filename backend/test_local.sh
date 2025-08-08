#!/bin/bash

# Local testing script for cloud functions

echo "🧪 Starting local cloud function testing..."

# Function to test a specific service
test_service() {
    local service_name=$1
    local port=$2
    
    echo "🚀 Starting $service_name on port $port..."
    
    cd functions/$service_name
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start the function
    echo "▶️  Running $service_name..."
    functions-framework --target=${service_name//-/_} --port=$port --debug &
    
    # Store PID for cleanup
    echo $! > ${service_name}.pid
    
    cd ../..
}

# Start all services on different ports
test_service "upload-service" 8080
test_service "embedding-service" 8081
test_service "data-service" 8082
test_service "search-service" 8083

echo "✅ All services started!"
echo ""
echo "📋 Service URLs:"
echo "   📤 Upload Service:    http://localhost:8080"
echo "   🧠 Embedding Service: http://localhost:8081"
echo "   💾 Data Service:      http://localhost:8082"
echo "   🔍 Search Service:    http://localhost:8083"
echo ""
echo "🛑 To stop all services, run: ./stop_local.sh"
