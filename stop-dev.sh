#!/bin/bash

# Packers Hub - Stop All Services Script
# This script stops all running Packers Hub services

echo "🛑 Stopping Packers Hub services..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

stopped_count=0

# Stop Vite Frontend
if pgrep -f "vite" > /dev/null; then
    echo -e "${YELLOW}⚛️  Stopping Vite Frontend...${NC}"
    pkill -f "vite"
    ((stopped_count++))
    sleep 1
fi

# Stop Uvicorn (FastAPI)
if pgrep -f "uvicorn" > /dev/null; then
    echo -e "${YELLOW}🚀 Stopping FastAPI Backend...${NC}"
    pkill -f "uvicorn"
    ((stopped_count++))
    sleep 1
fi

# Stop Celery Worker
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${YELLOW}⚙️  Stopping Celery Worker...${NC}"
    pkill -f "celery.*worker"
    ((stopped_count++))
    sleep 1
fi

# Stop Celery Beat
if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "${YELLOW}⏰ Stopping Celery Beat...${NC}"
    pkill -f "celery.*beat"
    ((stopped_count++))
    sleep 1
fi

echo ""

if [ $stopped_count -eq 0 ]; then
    echo -e "${YELLOW}ℹ️  No services were running${NC}"
else
    echo -e "${GREEN}✅ Stopped $stopped_count service(s)${NC}"
fi

echo ""
echo "All Packers Hub services have been stopped."
echo ""

# Optional: Close the Terminal windows that were opened
# Uncomment the following if you want to auto-close the Terminal windows
# osascript -e 'tell application "Terminal" to close (every window whose name contains "uvicorn")' 2>/dev/null
# osascript -e 'tell application "Terminal" to close (every window whose name contains "celery")' 2>/dev/null
# osascript -e 'tell application "Terminal" to close (every window whose name contains "vite")' 2>/dev/null
