# Use Python base image with CUDA support
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Step 1: Install basic tools (should be fast)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Step 2: Install software-properties-common (needed for PPA)
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Add deadsnakes PPA (this might be slow)
RUN add-apt-repository -y ppa:deadsnakes/ppa

# Step 4: Update package list after adding PPA
RUN apt-get update

# Step 5: Set timezone non-interactively (prevents prompts during install)
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Step 6: Install Python 3.9 (this might be slow)
RUN apt-get install -y --no-install-recommends \
    python3.9 \
    && rm -rf /var/lib/apt/lists/*

# Step 7: Install Python 3.9 dev packages and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9-dev \
    python3.9-distutils \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Step 8: Install runtime libraries (OpenMP, glib, OpenGL for opencv-python-headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y


# Step 9: Install pip for Python 3.9
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# Step 10: Create symlinks
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python

# Step 11: Upgrade pip and install build tools for pyproject.toml
RUN pip install --upgrade pip setuptools wheel build

# Copy requirements first for better caching
# This layer is cached unless requirements.txt changes
COPY requirements.txt /app/requirements.txt

# Install PyTorch with CUDA 12.4 support first
# This layer is cached unless PyTorch version changes
RUN pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# Install other Python dependencies
# This layer is cached unless requirements.txt changes
# Docker will reuse this layer if requirements.txt hasn't changed
# Use verbose output to see which package fails
RUN pip install --no-cache-dir -v -r requirements.txt

# Install LightGlue (copy and install before application code for better caching)
# Create directory structure and copy light_glue directory
RUN mkdir -p /app/lightglue
COPY lightglue/light_glue /app/lightglue/light_glue
# Install LightGlue in editable mode
RUN cd /app/lightglue/light_glue && \
    ls -la && \
    test -f pyproject.toml && \
    pip install --no-cache-dir -e .

# Copy application code
COPY api.py run.py align.py utils.py data_config.py main_cd.py /app/
COPY models/ /app/models/
COPY datasets/ /app/datasets/
COPY misc/ /app/misc/

# Create directories (code will be mounted as volume in development)
RUN mkdir -p /app/checkpoints

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
# CUDA_VISIBLE_DEVICES is optional - set via docker-compose or docker run if GPU available

# Run the API server with device check
CMD sh -c "python -c 'import torch; print(\"🚀 Starting API server...\"); print(\"✅ GPU Available:\", torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"⚠️  Running on CPU (GPU not available - slower but will work)\"); print()' && uvicorn api:app --host 0.0.0.0 --port 8000"

