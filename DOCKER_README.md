# Docker Setup for Change Detection Application

This directory contains Docker configuration files to run both the Change Detection API (backend) and Frontend in containerized environments.

## Prerequisites

1. **Docker** installed (version 20.10 or later)
2. **Docker Compose** (optional, for easier management)
3. **NVIDIA Docker** (optional, for GPU support):
   - Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
   - Verify with: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`

## Quick Start

### Option 1: Using Docker Compose (Recommended)

The easiest way to run both services together:

```bash
# Start both services
docker-compose up -d

# Or with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Using Start Scripts (Docker Compose)

These scripts use docker-compose to manage both services together:

**Linux/Mac:**
```bash
# Make executable (first time only)
chmod +x start.sh

# Start both services
./start.sh

# Start with rebuild
./start.sh --build

# Start with GPU support
./start.sh --gpu
```

**Windows:**
```cmd
# Start both services
start.bat

# Start with rebuild
start.bat --build

# Start with GPU support
start.bat --gpu
```

### Option 2b: Using Standalone Start Scripts

These scripts run containers separately using `host.docker.internal` for networking (useful when you want more control or are not using docker-compose):

**Linux/Mac:**
```bash
# Make executable (first time only)
chmod +x start-standalone.sh

# Start both services separately
./start-standalone.sh

# Start with rebuild
./start-standalone.sh --build

# Start with GPU support
./start-standalone.sh --gpu
```

**Windows:**
```cmd
# Start both services separately
start-standalone.bat

# Start with rebuild
start-standalone.bat --build

# Start with GPU support
start-standalone.bat --gpu
```

**Note:** The standalone scripts automatically handle `host.docker.internal` networking:
- On Linux: Adds `--add-host=host.docker.internal:host-gateway` flag
- On Windows/Mac: Uses `host.docker.internal` automatically (Docker Desktop feature)

### Option 3: Running Backend and Frontend Separately

If you want to run the containers separately (useful for development or when you need more control):

#### Backend

1. **Build the backend image:**
   ```bash
   docker build -t change-detection-backend .
   ```

2. **Run the backend container:**
   
   **With GPU:**
   ```bash
   docker run -d --name change-detection-backend \
     --gpus all \
     -p 8000:8000 \
     -v $(pwd)/checkpoints:/app/checkpoints \
     -v $(pwd):/app \
     change-detection-backend
   ```
   
   **CPU only (no GPU):**
   ```bash
   docker run -d --name change-detection-backend \
     -p 8000:8000 \
     -v $(pwd)/checkpoints:/app/checkpoints \
     -v $(pwd):/app \
     change-detection-backend
   ```

   **Windows (PowerShell):**
   ```powershell
   docker run -d --name change-detection-backend `
     -p 8000:8000 `
     -v ${PWD}/checkpoints:/app/checkpoints `
     -v ${PWD}:/app `
     change-detection-backend
   ```

#### Frontend

1. **Build the frontend image:**
   ```bash
   cd frontend
   docker build -t change-detection-frontend .
   cd ..
   ```

2. **Run the frontend container:**
   
   **Linux/Mac:**
   ```bash
   docker run -d --name change-detection-frontend \
     -p 3000:80 \
     --add-host=host.docker.internal:host-gateway \
     change-detection-frontend
   ```
   
   **Windows (Docker Desktop):**
   ```powershell
   docker run -d --name change-detection-frontend `
     -p 3000:80 `
     change-detection-frontend
   ```
   
   **Note:** On Windows Docker Desktop, `host.docker.internal` works automatically. On Linux, you need the `--add-host=host.docker.internal:host-gateway` flag.

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

#### Stop Separate Containers

```bash
# Stop and remove containers
docker stop change-detection-backend change-detection-frontend
docker rm change-detection-backend change-detection-frontend
```

## API Documentation

Once the backend container is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### GPU Support

The Dockerfile is configured for CUDA 12.4. The application automatically falls back to CPU if GPU is not available.

To enable GPU support:
1. Install NVIDIA Container Toolkit
2. Use `--gpus all` flag when running the backend container
3. Or uncomment the GPU section in `docker-compose.yml`

### Checkpoints

The checkpoints directory is mounted as a volume. Make sure your checkpoints are in the `./checkpoints/` directory before running. If checkpoints don't exist, they will be automatically downloaded on first run.

### Environment Variables

You can customize behavior with environment variables:

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: empty, auto-detects)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

Example:
```bash
docker run -d -p 8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  change-detection-backend
```

## Troubleshooting

### GPU not detected

1. Verify NVIDIA Docker is installed:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
   ```

2. The application will automatically use CPU if GPU is not available - check logs for device detection messages

### Frontend can't connect to backend (405 errors)

If running containers separately:
- Make sure backend is running on port 8000
- On Linux, use `--add-host=host.docker.internal:host-gateway` when running frontend
- On Windows/Mac Docker Desktop, `host.docker.internal` works automatically
- Or use docker-compose which handles networking automatically

### Port already in use

Change the port mapping:
```bash
# Backend on different port
docker run -p 8001:8000 ...

# Frontend on different port
docker run -p 3001:80 ...
```

### Out of memory errors

- Reduce batch size in the API call
- Use CPU mode if GPU memory is insufficient
- Adjust `img_size` parameter to process smaller images

## Building for Production

For production deployment, consider:

1. Using specific image tags instead of `latest`
2. Setting up proper logging
3. Adding health checks (already included)
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
