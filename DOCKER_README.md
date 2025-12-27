# Docker Setup for Change Detection API

This directory contains Docker configuration files to run the Change Detection API in a containerized environment.

## Prerequisites

1. **Docker** installed (version 20.10 or later)
2. **Docker Compose** (optional, for easier management)
3. **NVIDIA Docker** (for GPU support):
   - Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
   - Verify with: `docker run --rm --gpus all nvidia/cuda:11.7-base-ubuntu22.04 nvidia-smi`

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

The API will be available at `http://localhost:8000`

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t change-detection-api .
   ```

2. **Run the container:**
   ```bash
   docker run --gpus all -p 8000:8000 \
     -v $(pwd)/checkpoints:/app/checkpoints:ro \
     change-detection-api
   ```

   For CPU-only (no GPU):
   ```bash
   docker run -p 8000:8000 \
     -v $(pwd)/checkpoints:/app/checkpoints:ro \
     change-detection-api
   ```

## API Documentation

Once the container is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### GPU Support

The Dockerfile is configured for CUDA 11.7. If you need a different CUDA version:

1. Update the base image in `Dockerfile`:
   ```dockerfile
   FROM pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
   ```

2. Rebuild the image

### Checkpoints

The checkpoints directory is mounted as a read-only volume. Make sure your checkpoints are in the `./checkpoints/` directory before running.

### Environment Variables

You can customize behavior with environment variables:

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: `0`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

Example:
```bash
docker run --gpus all -p 8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v $(pwd)/checkpoints:/app/checkpoints:ro \
  change-detection-api
```

## Troubleshooting

### GPU not detected

1. Verify NVIDIA Docker is installed:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.7-base-ubuntu22.04 nvidia-smi
   ```

2. Check docker-compose.yml has GPU configuration

### Out of memory errors

- Reduce batch size in the API call
- Use CPU mode if GPU memory is insufficient
- Adjust `img_size` parameter to process smaller images

### Port already in use

Change the port mapping in docker-compose.yml or use a different port:
```bash
docker run -p 8001:8000 ...
```

## Building for Production

For production deployment, consider:

1. Using a specific tag instead of `latest`
2. Setting up proper logging
3. Adding health checks
4. Using a reverse proxy (nginx) in front of the API
5. Setting resource limits in docker-compose.yml

Example production docker-compose.yml additions:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

