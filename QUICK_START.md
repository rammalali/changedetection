# Quick Start Guide

## Start Both Frontend and Backend

### Option 1: Using Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# Or with build
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Using Start Scripts

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x start.sh

# Start services
./start.sh

# Start with rebuild
./start.sh --build

# Start with GPU support (if NVIDIA Container Toolkit installed)
./start.sh --gpu

# Start with both rebuild and GPU
./start.sh --build --gpu
```

**Windows:**
```cmd
# Start services
start.bat

# Start with rebuild
start.bat --build

# Start with GPU support
start.bat --gpu
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Services

- **Backend** (`change-detection-backend`): FastAPI service on port 8000
- **Frontend** (`change-detection-frontend`): Vue.js app served by Nginx on port 3000

## GPU Support

To enable GPU support, you need:
1. NVIDIA GPU with drivers installed
2. NVIDIA Container Toolkit installed
3. Uncomment the `deploy` section in `docker-compose.yml` (lines 23-29)

Or use the start script with `--gpu` flag.

## Troubleshooting

### Check if services are running:
```bash
docker-compose ps
```

### View logs:
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuild everything:
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Stop and remove everything:
```bash
docker-compose down -v
```

