#!/bin/bash

echo "🍽️  Starting Meal Planner - Full Stack Application"
echo "=================================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if backend port is available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
else
    echo "🚀 Starting backend with Docker..."
    cd /Users/jmwright/code/meal-planner
    docker-compose up --build -d
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 10
    
    # Test backend connection
    if curl -s http://localhost:8000/api/ > /dev/null; then
        echo "✅ Backend is running on http://localhost:8000"
    else
        echo "❌ Backend failed to start. Check Docker logs:"
        echo "   docker-compose logs backend"
        exit 1
    fi
fi

# Check if frontend port is available
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend might already be running."
    echo "   Frontend should be available at: http://localhost:3000"
else
    echo "🚀 Starting frontend..."
    cd /Users/jmwright/code/meal-planner/frontend
    npm start &
    FRONTEND_PID=$!
    
    echo "✅ Frontend is starting on http://localhost:3000"
    echo "   Process ID: $FRONTEND_PID"
fi

echo ""
echo "🎉 Application is starting up!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/api/"
echo ""
echo "To stop the application:"
echo "   Frontend: Ctrl+C or kill the npm process"
echo "   Backend:  docker-compose down"
