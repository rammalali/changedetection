# Change Detection Application

A satellite image change detection system using **ChangeFormer** and **LightGlue** for detecting changes between two time periods.

## How It Works

The application processes satellite images through a multi-scale change detection pipeline:

1. **Image Alignment**: LightGlue aligns images from two time periods
2. **Multi-Scale Detection**: ChangeFormer model runs multiple times at different resolutions
3. **Result Combination**: Masks from all calls are merged with confidence levels

### Processing Parameters

| Parameter | Purpose |
|-----------|---------|
| **Number of Model Calls** | Runs model multiple times: Call 1 at `img_size`, Call 2 at `img_size/2`, Call 3 at `img_size/4` |
| **Number of Crops per Side** | Divides image into pieces (only in calls > 1). Each piece = `current_img_size` for that call |

### Example: `img_size=1024`, `calls_nb=2`, `n=2`

**Call 1: Process full image at 1024×1024**
```
┌─────────────────┐
│                 │
│   1024×1024     │  → Processed at 1024×1024 → mask_1
│                 │
└─────────────────┘
```

**Call 2: Crop into 4 pieces (2×2), each 512×512**
```
┌─────────┬─────────┐
│ 512×512 │ 512×512 │  → Each processed at 512×512
├─────────┼─────────┤  → Combined → mask_2
│ 512×512 │ 512×512 │
└─────────┴─────────┘
```

**Final: Combine mask_1 + mask_2**
```
┌─────────────────┐
│                 │
│  Combined Mask  │  → Confidence levels:
│                 │     • 255 = detected in 2+ calls
│                 │     • 128 = detected in 1 call
│                 │     • 0   = no detection
└─────────────────┘
```

### Output Results

- **Mask**: Binary change detection mask
- **Color Mask**: Color-coded visualization
- **Overlay A/B**: Original images with change mask overlay

## Quick Start

### Running Both Services (Recommended)

The easiest way to run the complete application:

```bash
# Make executable (first time only)
chmod +x start.sh

# Start both services
./start.sh

# Start with rebuild
./start.sh --build

# Start with GPU support (if NVIDIA Container Toolkit is installed)
./start.sh --gpu
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**Stop services:**
```bash
docker-compose down
```

## Detailed Setup Instructions

### Backend API

For detailed instructions on running the backend API (Docker and Python), see:

📄 **[Backend Setup Guide](DOCKER_README.md#backend-api)**

The guide includes:
- **DOCKERFILE** setup and configuration
- Running with Docker
- Running with Python (without Docker)
- GPU support configuration
- API documentation

### Frontend

For detailed instructions on running the frontend (Docker and npm), see:

📄 **[Frontend Setup Guide](frontend/README.md)**

The guide includes:
- **DOCKERFILE** setup and configuration
- Running with Docker
- Running with npm (development)
- Build and deployment

## Technologies

- **Backend**: FastAPI, ChangeFormer, LightGlue, PyTorch
- **Frontend**: Vue.js 3, Vite
- **Containerization**: Docker, Docker Compose

## Test Data

Sample test images are provided in the `data/` folder:
- `data/A/` - "Before" images
- `data/B/` - "After" images

You can use these images to test the application through the web interface.

## Model Checkpoints

Model checkpoints are **automatically downloaded** on first startup if they don't exist in `./checkpoints/ChangeFormer_DSIFN/`.

Manual download: [DSIFN Weights](https://github.com/wgcban/ChangeFormer/releases/download/v0.1.0/CD_ChangeFormerV6_DSIFN_b16_lr0.00006_adamw_train_test_200_linear_ce_multi_train_True_multi_infer_False_shuffle_AB_False_embed_dim_256.zip)
