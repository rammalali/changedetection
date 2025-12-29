@echo off
REM Script to start both frontend and backend Docker containers on Windows
REM Usage: start.bat [--build] [--gpu]

setlocal enabledelayedexpansion

set BUILD=false
set GPU=false

REM Parse arguments
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--build" set BUILD=true
if "%~1"=="--gpu" set GPU=true
shift
goto parse_args
:end_parse

echo 🚀 Starting Change Detection Application...
echo.

REM Check if docker is available
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Docker is not installed or not in PATH
    exit /b 1
)

REM Use docker compose (newer) or docker-compose (older)
docker compose version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set COMPOSE_CMD=docker compose
) else (
    docker-compose --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set COMPOSE_CMD=docker-compose
    ) else (
        echo ❌ Error: docker-compose is not available
        exit /b 1
    )
)

REM Build if requested
if "%BUILD%"=="true" (
    echo 🔨 Building Docker images...
    %COMPOSE_CMD% build
    echo.
)

REM Check for GPU and NVIDIA Container Toolkit
echo 🔍 Checking for GPU and NVIDIA Container Toolkit...
set NVIDIA_CONTAINER_TOOLKIT=false

REM Check if nvidia-smi works on host
where nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    nvidia-smi >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ NVIDIA GPU detected on host
        
        REM Test if NVIDIA Container Toolkit is installed
        docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo    ✅ NVIDIA Container Toolkit is installed - GPU will be available in containers
            set NVIDIA_CONTAINER_TOOLKIT=true
        ) else (
            echo    ⚠️  NVIDIA Container Toolkit NOT installed - containers will run on CPU
            echo    💡 Install it with: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
            set NVIDIA_CONTAINER_TOOLKIT=false
        )
    ) else (
        echo    ⚠️  nvidia-smi found but GPU not accessible
        set NVIDIA_CONTAINER_TOOLKIT=false
    )
) else (
    echo    ℹ️  No GPU detected - will run on CPU
    set NVIDIA_CONTAINER_TOOLKIT=false
)

REM Create temporary docker-compose override for GPU if available
if "%GPU%"=="true" (
    echo 📦 Starting containers with GPU support...
    set CUDA_VISIBLE_DEVICES=0
    REM Create override file
    (
        echo version: '3.8'
        echo services:
        echo   backend:
        echo     deploy:
        echo       resources:
        echo         reservations:
        echo           devices:
        echo             - driver: nvidia
        echo               count: 1
        echo               capabilities: [gpu]
    ) > docker-compose.override.yml
) else if "%NVIDIA_CONTAINER_TOOLKIT%"=="true" (
    echo 📦 Starting containers with GPU support (auto-detected)...
    set CUDA_VISIBLE_DEVICES=0
    REM Create override file
    (
        echo version: '3.8'
        echo services:
        echo   backend:
        echo     deploy:
        echo       resources:
        echo         reservations:
        echo           devices:
        echo             - driver: nvidia
        echo               count: 1
        echo               capabilities: [gpu]
    ) > docker-compose.override.yml
) else (
    echo 📦 Starting containers on CPU...
    set CUDA_VISIBLE_DEVICES=
    REM Remove override file if it exists
    if exist docker-compose.override.yml del docker-compose.override.yml
)

%COMPOSE_CMD% up -d

echo.
echo ✅ Services started!
echo.
echo 📍 Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📊 View logs:
echo    %COMPOSE_CMD% logs -f
echo.
echo 🛑 Stop services:
echo    %COMPOSE_CMD% down
echo.

