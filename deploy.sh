#!/bin/bash

# UMatch Financial Control - Deployment Script
set -e

echo "🚀 UMatch Financial Control - Deployment"
echo "=========================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Step 1: Build frontend
echo ""
echo "📦 Step 1: Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Step 2: Build Docker image
echo ""
echo "🐳 Step 2: Building Docker image..."
docker build -t umatch-financial:latest .

# Step 3: Run with docker-compose
echo ""
echo "🔧 Step 3: Starting container..."
docker-compose up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Application is running at:"
echo "   http://localhost:8000"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
