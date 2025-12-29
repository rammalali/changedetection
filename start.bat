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

REM Start services
echo 📦 Starting containers...
if "%GPU%"=="true" (
    echo    GPU support enabled
    set CUDA_VISIBLE_DEVICES=0
) else (
    echo    Running on CPU (use --gpu flag if you have NVIDIA Container Toolkit)
    set CUDA_VISIBLE_DEVICES=
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

