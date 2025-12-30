# Backend API Setup Guide

This guide covers detailed instructions for running the backend API using Docker or Python.

## Backend API

### DOCKERFILE

The backend uses a multi-stage Dockerfile based on NVIDIA CUDA for GPU support:

**Key Features:**
- Base image: `nvidia/cuda:12.6.0-devel-ubuntu22.04`
- Python 3.9
- PyTorch 2.6.0 with CUDA 12.4 support
- LightGlue integration
- Automatic GPU detection

**DOCKERFILE Location:** `./Dockerfile`

### Option 1: Running with Docker

#### Prerequisites

- Docker (version 20.10 or later)
- NVIDIA Container Toolkit (for GPU support)
  - Install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
  - Verify: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`

#### Build and Run

**With GPU support:**
```bash
# Build the image
docker build -t change-detection-backend .

# Run the container
docker run -d --name change-detection-backend \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  change-detection-backend
```

**CPU only (no GPU):**
```bash
# Build the image
docker build -t change-detection-backend .

# Run the container
docker run -d --name change-detection-backend \
  -p 8000:8000 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  change-detection-backend
```

**Windows (PowerShell):**
```powershell
# Build
docker build -t change-detection-backend .

# Run
docker run -d --name change-detection-backend `
  -p 8000:8000 `
  -v ${PWD}/checkpoints:/app/checkpoints `
  change-detection-backend
```

#### View Logs
```bash
docker logs -f change-detection-backend
```

#### Stop Container
```bash
docker stop change-detection-backend
docker rm change-detection-backend
```

### Option 2: Running with Python (Without Docker)

#### Prerequisites

- Python 3.9
- pip package manager
- CUDA 12.4 (optional, for GPU support)

#### Installation Steps

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

#### Development Mode (with auto-reload)
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Once the backend is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Environment Variables

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: `0`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

### Checkpoints

Model checkpoints are automatically downloaded on first startup if they don't exist in `./checkpoints/ChangeFormer_DSIFN/`.

Manual download: [DSIFN Weights](https://github.com/wgcban/ChangeFormer/releases/download/v0.1.0/CD_ChangeFormerV6_DSIFN_b16_lr0.00006_adamw_train_test_200_linear_ce_multi_train_True_multi_infer_False_shuffle_AB_False_embed_dim_256.zip)

### Troubleshooting

**GPU not detected:**
- Verify NVIDIA Container Toolkit: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`
- The application will automatically fall back to CPU if GPU is not available

**Port already in use:**
- Change the port: `docker run -p 8001:8000 ...` or `uvicorn api:app --port 8001`

