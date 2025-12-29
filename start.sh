#!/bin/bash

# Script to start both frontend and backend Docker containers
# Usage: ./start.sh [--build] [--gpu]

set -e

BUILD=false
GPU=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --gpu)
            GPU=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./start.sh [--build] [--gpu]"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Change Detection Application..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Error: docker-compose is not available"
    exit 1
fi

# Build if requested
if [ "$BUILD" = true ]; then
    echo "🔨 Building Docker images..."
    $COMPOSE_CMD build
    echo ""
fi

# Check for GPU availability
echo "🔍 Checking for GPU..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        echo "   ✅ NVIDIA GPU detected"
        GPU_AVAILABLE=true
    else
        echo "   ⚠️  nvidia-smi found but GPU not accessible"
        GPU_AVAILABLE=false
    fi
else
    echo "   ℹ️  nvidia-smi not found (GPU may still work if NVIDIA Container Toolkit is installed)"
    GPU_AVAILABLE=false
fi

# Start services
echo "📦 Starting containers..."
if [ "$GPU" = true ] || [ "$GPU_AVAILABLE" = true ]; then
    echo "   🚀 GPU support enabled"
    export CUDA_VISIBLE_DEVICES=0
else
    echo "   💻 Running on CPU (GPU will be used automatically if NVIDIA Container Toolkit is installed)"
    export CUDA_VISIBLE_DEVICES=""
fi

$COMPOSE_CMD up -d

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs:"
echo "   $COMPOSE_CMD logs -f"
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD down"
echo ""

