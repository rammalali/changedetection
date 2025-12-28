# Change Detection Frontend

Vue.js frontend for the Change Detection API.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

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
- Results download as ZIP file

## Docker

### Build and Run with Docker

```bash
docker build -t change-detection-frontend .
docker run -p 3000:80 change-detection-frontend
```

### Using Docker Compose

```bash
docker-compose up -d
```

The frontend will be available at `http://localhost:3000`

## API Configuration

Make sure the backend API is running on `http://localhost:8000`. The frontend is configured to proxy requests to this endpoint.

**Note:** In production, you may need to configure nginx to proxy API requests or update the API endpoint in the frontend code.

