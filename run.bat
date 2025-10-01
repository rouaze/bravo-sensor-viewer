@echo off
setlocal EnableDelayedExpansion

REM Easy run script for Bravo Sensor Viewer v2.0.0 on Windows

echo.
echo ^🚀 Bravo Sensor Viewer v2.0.0 - Quick Start
echo ================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Check if Docker Compose is available  
docker compose version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    docker-compose --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ❌ Docker Compose is not available.
        pause
        exit /b 1
    )
    set DOCKER_COMPOSE=docker-compose
) else (
    set DOCKER_COMPOSE=docker compose
)

echo ✅ Docker is available

REM Parse command line arguments
set MODE=gui
set SERVICE=bravo-sensor-viewer

:parse_args
if "%~1"=="--test" (
    set MODE=test
    set SERVICE=bravo-sensor-test
    shift
    goto parse_args
)
if "%~1"=="--dev" (
    set MODE=dev
    set SERVICE=bravo-sensor-dev
    shift
    goto parse_args
)
if "%~1"=="--development" (
    set MODE=dev
    set SERVICE=bravo-sensor-dev
    shift
    goto parse_args
)
if "%~1"=="--console" (
    set MODE=console
    shift
    goto parse_args
)
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="/?" goto show_help

goto main

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --test              Run sensor tests only
echo   --dev, --development Run in development mode
echo   --console           Run without GUI
echo   -h, --help, /?      Show this help message
echo.
echo Examples:
echo   %0                  # Run GUI application
echo   %0 --test           # Run sensor tests  
echo   %0 --dev            # Development mode with hot reload
pause
exit /b 0

:main

REM Setup X11 forwarding for Windows (using VcXsrv or similar)
echo 🔧 Setting up display for GUI...
if not defined DISPLAY set DISPLAY=host.docker.internal:0.0
echo    DISPLAY set to: %DISPLAY%

echo 🏗️ Building Docker container...

REM Build the container
%DOCKER_COMPOSE% build --no-cache
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build Docker container
    pause
    exit /b 1
)

echo ✅ Container built successfully

REM Run based on mode
if "%MODE%"=="gui" (
    echo 🖥️ Starting GUI application...
    echo 📱 Connect your Bravo/Malacca/Spotlight 2 device now
    echo.
    echo 💡 For GUI to work on Windows, you need an X11 server like:
    echo    - VcXsrv ^(recommended^): https://sourceforge.net/projects/vcxsrv/
    echo    - Xming: https://sourceforge.net/projects/xming/
    echo.
    pause
    %DOCKER_COMPOSE% up --remove-orphans %SERVICE%
)

if "%MODE%"=="test" (
    echo 🧪 Running sensor tests...
    %DOCKER_COMPOSE% --profile testing up --remove-orphans %SERVICE%
)

if "%MODE%"=="dev" (
    echo 🛠️ Starting development environment...
    %DOCKER_COMPOSE% --profile development up --remove-orphans %SERVICE%
)

if "%MODE%"=="console" (
    echo 💻 Running console application...
    %DOCKER_COMPOSE% run --rm %SERVICE% python simple_sensor_test.py
)

echo ✨ Done!
pause