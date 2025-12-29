# Installing NVIDIA Container Toolkit

If you have an NVIDIA GPU and `nvidia-smi` works on your host, but Docker containers can't access it, you need to install NVIDIA Container Toolkit.

## Quick Installation (Ubuntu/Debian)

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker daemon
sudo systemctl restart docker

# Verify installation
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

If the last command shows your GPU information, NVIDIA Container Toolkit is installed correctly!

## For Other Linux Distributions

See the official installation guide:
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

## After Installation

Once installed, you can run:
```bash
./start.sh
```

The script will automatically detect NVIDIA Container Toolkit and enable GPU support in containers.

