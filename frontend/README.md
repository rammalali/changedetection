# Frontend Setup Guide

Vue.js frontend for the Change Detection API.

## DOCKERFILE

The frontend uses a multi-stage Docker build with nginx for production:

**Key Features:**
- Build stage: Node.js 18 Alpine for building the Vue app
- Production stage: nginx Alpine for serving static files
- Optimized nginx configuration for SPA routing
- Gzip compression enabled

**DOCKERFILE Location:** `./Dockerfile`

## Option 1: Running with Docker

### Build and Run

```bash
# Build the image
docker build -t change-detection-frontend .

# Run the container
docker run -d --name change-detection-frontend \
  -p 3000:80 \
  change-detection-frontend
```

**Windows (PowerShell):**
```powershell
# Build
docker build -t change-detection-frontend .

# Run
docker run -d --name change-detection-frontend `
  -p 3000:80 `
  change-detection-frontend
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The frontend will be available at `http://localhost:3000`

### View Logs
```bash
docker logs -f change-detection-frontend
```

### Stop Container
```bash
docker stop change-detection-frontend
docker rm change-detection-frontend
```

## Option 2: Running with npm (Development)

### Prerequisites

- Node.js 18 or later
- npm package manager

### Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Features

- Drag and drop image upload
- File browser upload
- Folder upload support
- Configurable processing options:
  - Image size (1024/512/256)
  - Number of crops per side (1/2/3)
  - Number of model calls (1/2/3)
  - Crop image option (True/False)
- Loading indicator during processing
- Results displayed directly in UI with download options

## API Configuration

Make sure the backend API is running on `http://localhost:8000`. The frontend is configured to proxy requests to this endpoint during development.

**Note:** In production with Docker, you may need to configure nginx to proxy API requests or update the API endpoint in the frontend code.

