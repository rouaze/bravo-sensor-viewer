#!/bin/bash

# Easy run script for Bravo Sensor Viewer v2.0.0
# Works on Linux and macOS with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Bravo Sensor Viewer v2.0.0 - Quick Start${NC}"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi

# Function to setup X11 forwarding (Linux)
setup_x11_linux() {
    echo -e "${YELLOW}🔧 Setting up X11 forwarding for GUI...${NC}"
    
    # Allow X11 connections from localhost
    xhost +local:docker 2>/dev/null || echo -e "${YELLOW}⚠️  Could not set xhost permissions. GUI may not work.${NC}"
    
    # Export DISPLAY variable
    export DISPLAY=${DISPLAY:-:0}
    echo "   DISPLAY set to: $DISPLAY"
}

# Function to setup X11 forwarding (macOS)
setup_x11_macos() {
    echo -e "${YELLOW}🔧 Setting up X11 forwarding for macOS...${NC}"
    
    # Check if XQuartz is running
    if ! pgrep -x "Xquartz" > /dev/null; then
        echo -e "${YELLOW}⚠️  XQuartz is not running. Please start XQuartz first.${NC}"
        echo "   Install XQuartz: https://www.xquartz.org/"
    fi
    
    # Get IP address for Docker Desktop
    export DISPLAY=host.docker.internal:0
    echo "   DISPLAY set to: $DISPLAY"
}

# Detect operating system
case "$(uname -s)" in
    Linux*)
        OS="Linux"
        setup_x11_linux
        ;;
    Darwin*)
        OS="macOS"
        setup_x11_macos
        ;;
    *)
        echo -e "${RED}❌ Unsupported operating system. Use Windows batch script for Windows.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Detected OS: $OS${NC}"

# Parse command line arguments
MODE="gui"
SERVICE="bravo-sensor-viewer"

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            MODE="test"
            SERVICE="bravo-sensor-test"
            shift
            ;;
        --dev|--development)
            MODE="dev"
            SERVICE="bravo-sensor-dev"
            shift
            ;;
        --console)
            MODE="console"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --test              Run sensor tests only"
            echo "  --dev, --development Run in development mode"
            echo "  --console           Run without GUI"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run GUI application"
            echo "  $0 --test           # Run sensor tests"
            echo "  $0 --dev            # Development mode with hot reload"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown parameter: $1${NC}"
            echo "Use $0 --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🏗️  Building Docker container...${NC}"

# Choose appropriate docker-compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Build the container
if ! $DOCKER_COMPOSE build --no-cache; then
    echo -e "${RED}❌ Failed to build Docker container${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Container built successfully${NC}"

# Run based on mode
case $MODE in
    "gui")
        echo -e "${BLUE}🖥️  Starting GUI application...${NC}"
        echo -e "${YELLOW}📱 Connect your Bravo/Malacca/Spotlight 2 device now${NC}"
        $DOCKER_COMPOSE up --remove-orphans $SERVICE
        ;;
    "test")
        echo -e "${BLUE}🧪 Running sensor tests...${NC}"
        $DOCKER_COMPOSE --profile testing up --remove-orphans $SERVICE
        ;;
    "dev")
        echo -e "${BLUE}🛠️  Starting development environment...${NC}"
        $DOCKER_COMPOSE --profile development up --remove-orphans $SERVICE
        ;;
    "console")
        echo -e "${BLUE}💻 Running console application...${NC}"
        $DOCKER_COMPOSE run --rm $SERVICE python simple_sensor_test.py
        ;;
esac

echo -e "${GREEN}✨ Done!${NC}"