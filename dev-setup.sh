#!/bin/bash

# Development environment setup for Bravo Sensor Viewer v2.0.0
# Sets up local development without Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛠️ Bravo Sensor Viewer v2.0.0 - Development Setup${NC}"
echo "====================================================="

# Check Python version
echo -e "${YELLOW}🐍 Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.7+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment active: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment detected. Creating one...${NC}"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
fi

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Requirements installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Install pyhidpp package in development mode
echo -e "${YELLOW}📦 Installing pyhidpp in development mode...${NC}"
cd Vibration_test_scripts/pyhidpp
pip install -e .
cd ../..
echo -e "${GREEN}✅ pyhidpp installed in development mode${NC}"

# Install additional development tools
echo -e "${YELLOW}📦 Installing development tools...${NC}"
pip install --upgrade \
    pyinstaller \
    black \
    flake8 \
    pytest \
    pytest-qt \
    pre-commit

echo -e "${GREEN}✅ Development tools installed${NC}"

# Setup pre-commit hooks (optional)
echo -e "${YELLOW}🪝 Setting up pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120, --extend-ignore=E203,W503]

  - repo: local
    hooks:
      - id: version-check
        name: Version consistency check
        entry: python -c "from version import __version__; print(f'Version: {__version__}')"
        language: system
        pass_filenames: false
EOF

    pre-commit install
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  pre-commit not available, skipping hooks setup${NC}"
fi

# Setup directories
echo -e "${YELLOW}📁 Creating development directories...${NC}"
mkdir -p logs config tests

# Create a simple test
cat > tests/test_version.py << 'EOF'
"""Test version information"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from version import __version__, __build_date__, __author__

def test_version_format():
    """Test that version follows semantic versioning"""
    parts = __version__.split('.')
    assert len(parts) >= 2, "Version should have at least major.minor"
    
def test_version_components():
    """Test version components are not empty"""
    assert __version__, "Version should not be empty"
    assert __build_date__, "Build date should not be empty"
    assert __author__, "Author should not be empty"
    
def test_version_values():
    """Test expected version values"""
    assert __version__ == "2.0.0"
    assert __author__ == "Pierre Rouaze"
EOF

echo -e "${GREEN}✅ Development directories and tests created${NC}"

# Check system dependencies
echo -e "${YELLOW}🔍 Checking system dependencies...${NC}"

# Check for Qt5 libraries (Linux)
if command -v dpkg-query &> /dev/null; then
    if dpkg-query -W -f='${Status}' python3-pyqt5 2>/dev/null | grep -q "ok installed"; then
        echo -e "${GREEN}✅ PyQt5 system package found${NC}"
    else
        echo -e "${YELLOW}⚠️  PyQt5 system package not found. Install with: sudo apt-get install python3-pyqt5${NC}"
    fi
fi

# Check for USB/HID libraries
if [[ -f "/usr/include/hidapi/hidapi.h" ]] || [[ -f "/usr/local/include/hidapi/hidapi.h" ]]; then
    echo -e "${GREEN}✅ HIDAPI development headers found${NC}"
else
    echo -e "${YELLOW}⚠️  HIDAPI development headers not found.${NC}"
    echo -e "${YELLOW}   Install with: sudo apt-get install libhidapi-dev (Ubuntu/Debian)${NC}"
    echo -e "${YELLOW}             or: brew install hidapi (macOS)${NC}"
fi

# Test import of key modules
echo -e "${YELLOW}🧪 Testing key module imports...${NC}"
python3 -c "
try:
    import PyQt5.QtWidgets
    print('✅ PyQt5 import successful')
except ImportError as e:
    print(f'❌ PyQt5 import failed: {e}')

try:
    import matplotlib
    print('✅ Matplotlib import successful')
except ImportError as e:
    print(f'❌ Matplotlib import failed: {e}')

try:
    import numpy
    print('✅ NumPy import successful')
except ImportError as e:
    print(f'❌ NumPy import failed: {e}')

try:
    from pyhidpp.core.devices_manager import DevicesManager
    print('✅ pyhidpp import successful')
except ImportError as e:
    print(f'❌ pyhidpp import failed: {e}')

try:
    from version import __version__
    print(f'✅ Version module import successful: {__version__}')
except ImportError as e:
    print(f'❌ Version module import failed: {e}')
"

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Quick start commands:${NC}"
echo "  python bravo_sensor_viewer.py    # Run GUI application"
echo "  python simple_sensor_test.py     # Run console test"
echo "  python bravo_device_test.py      # Run device discovery test"
echo "  pytest tests/                    # Run tests"
echo "  black .                          # Format code"
echo "  flake8 .                         # Check code style"
echo ""
echo -e "${YELLOW}📖 For Docker setup, see README.md or run ./run.sh${NC}"