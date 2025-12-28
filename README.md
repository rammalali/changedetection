# Change Detection Project

A satellite image change detection system using **ChangeFormer** and **LightGlue**, built with **Python 3.9**.

## Project Overview

This project consists of:
- **Backend**: FastAPI service for change detection using ChangeFormer model and LightGlue for image alignment
- **Frontend**: Vue.js web interface for uploading and processing satellite images

### Technologies
- **Python 3.9**
- **ChangeFormer**: Deep learning model for change detection
- **LightGlue**: Feature matching and image alignment
- **FastAPI**: Backend API framework
- **Vue.js**: Frontend framework

## Prerequisites

- **Docker** (version 20.10 or later)
- **Docker Compose** (optional, for easier management)
- **NVIDIA Docker** (for GPU support):
  - Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
  - Verify with: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`

## Running the Backend Docker

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
The backend API will be available at `http://localhost:8000`

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t change-detection-api .
   ```

2. **Run the container with GPU support:**
   ```bash
   docker run --gpus all -p 8000:8000 \
     -v $(pwd):/app \
     -v $(pwd)/checkpoints:/app/checkpoints \
     change-detection-api
   ```

   **For CPU-only (no GPU):**
   ```bash
   docker run -p 8000:8000 \
     -v $(pwd):/app \
     -v $(pwd)/checkpoints:/app/checkpoints \
     change-detection-api
   ```

### Backend API Documentation

Once the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running the Frontend Docker

### Option 1: Using Docker Compose (Recommended)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the service:**
   ```bash
   docker-compose down
   ```

The frontend will be available at `http://localhost:3000`

### Option 2: Using Docker directly

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Build the image:**
   ```bash
   docker build -t change-detection-frontend .
   ```

3. **Run the container:**
   ```bash
   docker run -p 3000:80 change-detection-frontend
   ```

## Running Both Services Together

To run both backend and frontend simultaneously:

1. **Start the backend** (from project root):
   ```bash
   docker-compose up -d
   ```

2. **Start the frontend** (from frontend directory):
   ```bash
   cd frontend
   docker-compose up -d
   ```

Both services will be available:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## Configuration

### Backend Environment Variables

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: `0`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

### Checkpoints

Make sure your model checkpoints are in the `./checkpoints/` directory before running the backend. The checkpoints directory is mounted as a volume in the Docker container.

## Troubleshooting

### GPU not detected

1. Verify NVIDIA Docker is installed:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
   ```

2. Check that `docker-compose.yml` has GPU configuration

### Port already in use

Change the port mapping in `docker-compose.yml` or use a different port:
```bash
docker run -p 8001:8000 ...
```

### Frontend cannot connect to backend

Ensure the backend is running and accessible at `http://localhost:8000`. The frontend is configured to proxy API requests to this endpoint.

## Notes

- The backend uses **Python 3.9** with CUDA 12.4 support
- **ChangeFormer** model is used for change detection
- **LightGlue** is integrated for image alignment and feature matching
- Both services can be run independently or together

