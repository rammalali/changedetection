# Use Python base image with CUDA support
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python 3.9 and system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.9
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# Create symlinks for python
RUN ln -s /usr/bin/python3.9 /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements-docker.txt /app/requirements-docker.txt

# Install PyTorch with CUDA 12.4 support first
RUN pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# Install other Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install LightGlue
# Copy the entire lightglue directory structure
COPY lightglue /app/lightglue
RUN cd /app/lightglue/light_glue && pip install -e .

# Copy application code
COPY . /app/

# Make sure checkpoints directory exists (will be mounted or copied)
RUN mkdir -p /app/checkpoints

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Run the API server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

