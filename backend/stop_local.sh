#!/bin/bash

echo "🛑 Stopping all local cloud functions..."

# Stop all running functions
for service in upload-service embedding-service data-service search-service; do
    if [ -f "functions/$service/$service.pid" ]; then
        pid=$(cat "functions/$service/$service.pid")
        echo "Stopping $service (PID: $pid)..."
        kill $pid 2>/dev/null
        rm "functions/$service/$service.pid"
    fi
done

# Kill any remaining functions-framework processes
pkill -f "functions-framework" 2>/dev/null

echo "✅ All services stopped!"
