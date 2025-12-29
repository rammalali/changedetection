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

# Check for GPU and NVIDIA Container Toolkit
echo "🔍 Checking for GPU and NVIDIA Container Toolkit..."
NVIDIA_CONTAINER_TOOLKIT=false

# Check if nvidia-smi works on host
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "   ✅ NVIDIA GPU detected on host"
    
    # Test if NVIDIA Container Toolkit is installed (Docker can access GPU)
    if docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo "   ✅ NVIDIA Container Toolkit is installed - GPU will be available in containers"
        NVIDIA_CONTAINER_TOOLKIT=true
    else
        echo "   ⚠️  NVIDIA Container Toolkit NOT installed - containers will run on CPU"
        echo "   💡 Install it with: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
        NVIDIA_CONTAINER_TOOLKIT=false
    fi
else
    echo "   ℹ️  No GPU detected - will run on CPU"
    NVIDIA_CONTAINER_TOOLKIT=false
fi

# Create temporary docker-compose override for GPU if available
if [ "$GPU" = true ] || [ "$NVIDIA_CONTAINER_TOOLKIT" = true ]; then
    echo "📦 Starting containers with GPU support..."
    export CUDA_VISIBLE_DEVICES=0
    # Create temporary override file to enable GPU
    cat > docker-compose.override.yml <<EOF
version: '3.8'
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
EOF
else
    echo "📦 Starting containers on CPU..."
    export CUDA_VISIBLE_DEVICES=""
    # Remove override file if it exists
    rm -f docker-compose.override.yml
fi

$COMPOSE_CMD up -d

# Clean up override file after starting (optional, can leave it)
# rm -f docker-compose.override.yml

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

