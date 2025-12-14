#!/bin/bash

# Packers Hub - Quick Start Script
# This script helps you start all services for development

echo "🏈 Starting Packers Hub..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists in backend
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env file not found${NC}"
    echo ""
    echo "Please create backend/.env with:"
    echo "MONGO_URL=mongodb://localhost:27017/"
    echo "DATABASE_NAME=packers_hub"
    echo "API_KEY=your_api_sports_key"
    echo "REDIS_URL=redis://localhost:6379/0"
    exit 1
fi

# Check if Redis is running (required for Celery)
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: Redis is not responding${NC}"
    echo "   Start it with: brew services start redis"
    echo ""
fi

# Check if node_modules exists in frontend
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

echo -e "${GREEN}✅ Starting services...${NC}"
echo ""
echo "This will start 4 terminals:"
echo "  1️⃣  FastAPI Backend (port 8000)"
echo "  2️⃣  Celery Worker"
echo "  3️⃣  Celery Beat (scheduler)"
echo "  4️⃣  Vite Frontend (port 5173)"
echo ""
echo -e "${YELLOW}Press Ctrl+C in each terminal to stop${NC}"
echo ""

# macOS specific: Open new terminal windows
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Backend API
    osascript <<EOF
tell application "Terminal"
    do script "cd \"$PWD/backend\" && source .venv/bin/activate && echo '🚀 Starting FastAPI Backend...' && uvicorn app.main:app --reload"
end tell
EOF

    sleep 2

    # Celery Worker
    osascript <<EOF
tell application "Terminal"
    do script "cd \"$PWD/backend\" && source .venv/bin/activate && echo '⚙️  Starting Celery Worker...' && celery -A app.celery_app.celery_app worker --loglevel=info"
end tell
EOF

    sleep 2

    # Celery Beat
    osascript <<EOF
tell application "Terminal"
    do script "cd \"$PWD/backend\" && source .venv/bin/activate && echo '⏰ Starting Celery Beat...' && celery -A app.celery_app.celery_app beat --loglevel=info"
end tell
EOF

    sleep 2

    # Frontend
    osascript <<EOF
tell application "Terminal"
    do script "cd \"$PWD/frontend\" && echo '⚛️  Starting Vite Frontend...' && npm run dev"
end tell
EOF

    echo -e "${GREEN}✅ All services started in separate Terminal windows!${NC}"
    echo ""
    echo "Access the app at: http://localhost:5173"
    echo "API docs at: http://localhost:8000/docs"
    echo ""
    echo "To stop all services, close each Terminal window or press Ctrl+C in each"
else
    echo -e "${RED}This script is designed for macOS${NC}"
    echo ""
    echo "Please start services manually:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
    echo "Terminal 2 (Celery Worker):"
    echo "  cd backend && source .venv/bin/activate && celery -A app.celery_app.celery_app worker --loglevel=info"
    echo ""
    echo "Terminal 3 (Celery Beat):"
    echo "  cd backend && source .venv/bin/activate && celery -A app.celery_app.celery_app beat --loglevel=info"
    echo ""
    echo "Terminal 4 (Frontend):"
    echo "  cd frontend && npm run dev"
fi
