#!/bin/bash

# WeatherBot Development Startup Script

echo "🚀 Starting WeatherBot Development Environment..."
echo ""

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the WeatherBot root directory"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
echo "🔍 Checking ports..."
if ! check_port 8000; then
    echo "Backend port 8000 is already in use. Please stop the existing process."
fi

if ! check_port 3000; then
    echo "Frontend port 3000 is already in use. Please stop the existing process."
fi

echo ""

# Start backend
echo "🔧 Starting Backend (FastAPI)..."
cd backend
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please set up the backend first."
    echo "Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and start backend in background
source venv/bin/activate
echo "✅ Backend virtual environment activated"
python run.py &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Frontend (React)..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install --legacy-peer-deps
fi

echo "✅ Starting React development server..."
npm start &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"

echo ""
echo "🎉 WeatherBot is starting up!"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "🌐 Frontend App: http://localhost:3000"
echo "📊 API Health: http://localhost:8000/health"
echo ""
echo "💡 To stop both services, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping WeatherBot services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    echo "👋 WeatherBot development environment stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for processes
wait 