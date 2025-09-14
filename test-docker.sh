#!/bin/bash

echo "Testing Docker setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Docker is not running. Please start Docker first."
    exit 1
fi

echo "Docker is available and running."

# Build the backend image
echo "Building backend image..."
cd backend
docker build -t meal-planner-backend .

if [ $? -eq 0 ]; then
    echo "Backend image built successfully!"
    
    # Test running the container
    echo "Testing container..."
    docker run --rm -p 8000:8000 meal-planner-backend &
    CONTAINER_PID=$!
    
    # Wait a moment for the container to start
    sleep 5
    
    # Test if the API is responding
    if curl -s http://localhost:8000/api/ > /dev/null; then
        echo "✅ Backend is running successfully!"
    else
        echo "❌ Backend is not responding"
    fi
    
    # Stop the container
    kill $CONTAINER_PID
    docker stop $(docker ps -q --filter ancestor=meal-planner-backend) 2>/dev/null || true
    
else
    echo "❌ Failed to build backend image"
    exit 1
fi

echo "Docker setup test completed!"
