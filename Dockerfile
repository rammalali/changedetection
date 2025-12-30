FROM nvidia/cuda:12.6.0-devel-ubuntu22.04

WORKDIR /app

# Set environment variables early
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONUNBUFFERED=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/compat:/usr/local/lib:$LD_LIBRARY_PATH

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies and Python 3.9
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.9 \
        python3.9-dev \
        python3.9-distutils \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        pkg-config \
        libgomp1 \
        libglib2.0-0 \
        libgl1 \
        ffmpeg \
        libsm6 \
        libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Install pip and set up Python
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python && \
    pip install --upgrade pip setuptools wheel build

# Install Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir \
        torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124 && \
    pip install --no-cache-dir -r requirements.txt

# Install LightGlue (cached unless lightglue changes)
COPY lightglue/light_glue /app/lightglue/light_glue
RUN pip install --no-cache-dir -e /app/lightglue/light_glue

# Copy application code
COPY api.py run.py align.py utils.py data_config.py /app/
COPY models/ /app/models/
COPY datasets/ /app/datasets/
COPY misc/ /app/misc/

# Create required directories
RUN mkdir -p /app/checkpoints

EXPOSE 8000

CMD sh -c "python -c \"import torch; print('🚀 Starting API server...'); print('✅ GPU Available:', torch.cuda.get_device_name(0)) if torch.cuda.is_available() else print('⚠️  Running on CPU (GPU not available - slower but will work)'); print()\" && uvicorn api:app --host 0.0.0.0 --port 8000"

