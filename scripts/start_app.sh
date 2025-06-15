#!/bin/bash

echo "🏠 Real Estate Open Home Optimizer - Full Stack Startup"
echo "=================================================="

# Make scripts executable
chmod +x scripts/start_backend.sh
chmod +x scripts/start_clean_backend.sh
chmod +x scripts/start_frontend.sh

echo "🔧 Starting clean backend server in background (no scraping)..."
./scripts/start_clean_backend.sh &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🌐 Starting frontend development server..."
./scripts/start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "🎉 Application is starting up!"
echo "=================================================="
echo "📍 Backend API: http://localhost:5001"
echo "🌐 Frontend App: http://localhost:3000"
echo "🔍 Health Check: http://localhost:5001/api/health"
echo "🧪 Mock Data: http://localhost:5001/api/mock-data"
echo "=================================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait