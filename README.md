# Change Detection Project

An image change detection system using **ChangeFormer** and **LightGlue**, built with **Python 3.9**.

## Project Overview

This project consists of:
- **Backend**: FastAPI service for change detection using ChangeFormer model and LightGlue for image alignment
- **Frontend**: Vue.js web interface for uploading and processing aerial images

### Technologies
- **Python 3.9**
- **ChangeFormer**: Deep learning model for change detection
- **LightGlue**: Feature matching and image alignment
- **FastAPI**: Backend API framework
- **Vue.js**: Frontend framework

## Prerequisites

### For Docker Setup
- **Docker** (version 20.10 or later)
- **Docker Compose** (optional, for easier management)
- **NVIDIA Docker** (for GPU support):
  - Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
  - Verify with: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`

### For Non-Docker Setup
- **Python 3.9**
- **CUDA 12.4** (for GPU support, optional)
- **pip** package manager

## Running the Backend

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

### Option 2: Running without Docker (using uvicorn)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install PyTorch with CUDA support (if using GPU):**
   ```bash
   pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
   ```
   
   **For CPU-only:**
   ```bash
   pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
   ```

3. **Install LightGlue:**
   ```bash
   cd lightglue/light_glue
   pip install -e .
   cd ../..
   ```

4. **Run the API server:**
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

The backend API will be available at `http://localhost:8000`

### Backend API Documentation

Once the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running the Frontend

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

### Option 2: Using npm (Development)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000` (or the port specified in your Vite configuration)

## Running Both Services Together

### Using Docker Compose

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

### Mixed Setup (Backend without Docker, Frontend with Docker)

1. **Start the backend** (from project root, following Option 2 above):
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (from frontend directory):
   ```bash
   cd frontend
   docker-compose up -d
   ```

## Configuration

### Backend Environment Variables

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: `0`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

### Checkpoints

The model checkpoints will be **automatically downloaded** on first startup if they don't exist in the `./checkpoints/` directory. The weights are downloaded from:
[DSIFN Weights](https://github.com/wgcban/ChangeFormer/releases/download/v0.1.0/CD_ChangeFormerV6_DSIFN_b16_lr0.00006_adamw_train_test_200_linear_ce_multi_train_True_multi_infer_False_shuffle_AB_False_embed_dim_256.zip)

If you prefer to download them manually, you can download the zip file from the URL above and extract the checkpoint files (`best_ckpt.pt`, `last_ckpt.pt`, `log.txt`, `val_acc.npy`, `train_acc.npy`) to the `./checkpoints/ChangeFormer_DSIFN/` directory.

When using Docker, the checkpoints directory is mounted as a volume in the Docker container.

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
docker run -p 8000:8000 ...
```

### Frontend cannot connect to backend

Ensure the backend is running and accessible at `http://localhost:8000`. The frontend is configured to proxy API requests to this endpoint.

## Notes

- The backend uses **Python 3.9** with CUDA 12.4 support
- **ChangeFormer** model is used for change detection
- **LightGlue** is integrated for image alignment and feature matching
- Both services can be run independently or together

