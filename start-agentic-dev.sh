#!/bin/bash

# WeatherBot Agentic Development Server Startup Script
echo "🚀 Starting WeatherBot Agentic Development Servers..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    wait
    echo -e "${GREEN}All servers stopped.${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start backend server
echo -e "${BLUE}Starting Agentic Backend Server (Port 8000)...${NC}"
cd backend
source venv/bin/activate
python app/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo -e "${GREEN}✅ Agentic Backend is running successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting...${NC}"
fi

# Start frontend server
echo -e "${BLUE}Starting Frontend Server (Port 3000)...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 | grep -q "html"; then
    echo -e "${GREEN}✅ Frontend is running successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
fi

echo -e "\n${GREEN}🌤️  WeatherBot Agentic System is running!${NC}"
echo -e "${BLUE}📱 Frontend: ${NC}http://localhost:3000"
echo -e "${BLUE}🔧 Backend API: ${NC}http://localhost:8000"
echo -e "${BLUE}💚 Health Check: ${NC}http://localhost:8000/health"
echo -e "\n${YELLOW}Features:${NC}"
echo -e "  🤖 Agentic AI with memory and context"
echo -e "  🌍 Current weather and forecasts"
echo -e "  🌬️  Air quality information"
echo -e "  💬 Conversational interface"
echo -e "  🎯 Smart location memory"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for background processes
wait 