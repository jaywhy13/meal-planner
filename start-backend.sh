#!/bin/bash

echo "🍽️  Starting Meal Planner Backend with Docker..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is available and running."

# Choose setup type
echo ""
echo "Choose your setup:"
echo "1) Simple setup (SQLite) - Good for development"
echo "2) Production setup (PostgreSQL) - Good for production"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🚀 Starting simple setup with SQLite..."
        docker-compose up --build
        ;;
    2)
        echo "🚀 Starting production setup with PostgreSQL..."
        docker-compose -f docker-compose.prod.yml up --build
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
