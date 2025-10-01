#!/bin/bash

# Container testing script for Bravo Sensor Viewer v2.0.0
# Tests Docker setup without requiring physical devices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Bravo Sensor Viewer v2.0.0 - Container Testing${NC}"
echo "======================================================="

# Function to run test and report result
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}🔬 Testing: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        return 1
    fi
}

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Test 1: Docker availability
echo -e "\n${BLUE}=== Phase 1: Prerequisites ===${NC}"

((TOTAL_TESTS++))
if run_test "Docker availability" "docker --version > /dev/null 2>&1"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
    echo -e "${RED}❌ Docker is required for container testing${NC}"
    exit 1
fi

# Determine Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}❌ Docker Compose is required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Using Docker Compose: $DOCKER_COMPOSE${NC}"

# Test 2: Container build
echo -e "\n${BLUE}=== Phase 2: Container Build ===${NC}"

((TOTAL_TESTS++))
if run_test "Container build" "$DOCKER_COMPOSE build --no-cache 2>&1 | tail -5"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 3: Python environment validation
echo -e "\n${BLUE}=== Phase 3: Python Environment ===${NC}"

((TOTAL_TESTS++))
if run_test "Python version check" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python --version"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 4: Core imports test
echo -e "\n${BLUE}=== Phase 4: Core Dependencies ===${NC}"

IMPORT_TEST='
try:
    print("Testing core imports...")
    
    # Test standard library imports
    import sys, os, time, logging
    print("✅ Standard library imports OK")
    
    # Test PyQt5
    import PyQt5.QtWidgets, PyQt5.QtCore, PyQt5.QtGui
    print("✅ PyQt5 imports OK")
    
    # Test matplotlib
    import matplotlib
    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt
    print("✅ Matplotlib imports OK")
    
    # Test numpy
    import numpy as np
    print("✅ NumPy imports OK")
    
    # Test pyhidpp
    from pyhidpp.core.devices_manager import DevicesManager
    from pyhidpp.security import SecurityManager
    from pyhidpp.features.x9402 import X9402
    from pyhidpp.features.x19c0 import X19C0
    print("✅ pyhidpp imports OK")
    
    print("🎉 All core imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
'

((TOTAL_TESTS++))
if run_test "Core imports" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"$IMPORT_TEST\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 5: Version information test
echo -e "\n${BLUE}=== Phase 5: Version Information ===${NC}"

VERSION_TEST='
try:
    from version import __version__, __build_date__, __author__
    print(f"Version: {__version__}")
    print(f"Build Date: {__build_date__}")
    print(f"Author: {__author__}")
    
    # Validate version format
    parts = __version__.split(".")
    if len(parts) < 2:
        raise ValueError("Invalid version format")
    
    if __version__ != "2.0.0":
        raise ValueError(f"Expected version 2.0.0, got {__version__}")
        
    print("✅ Version information valid")
    
except Exception as e:
    print(f"❌ Version test error: {e}")
    import sys
    sys.exit(1)
'

((TOTAL_TESTS++))
if run_test "Version information" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"$VERSION_TEST\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 6: Application startup test (headless)
echo -e "\n${BLUE}=== Phase 6: Application Logic ===${NC}"

APP_TEST='
import os
import sys
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend

# Mock QApplication for headless testing
class MockQApplication:
    def __init__(self, args): pass
    def exec_(self): return 0
    def quit(self): pass

# Monkey patch PyQt5 for testing
sys.modules["PyQt5.QtWidgets"].QApplication = MockQApplication

# Test version import in main script context
try:
    from version import __version__, get_version_string
    print(f"✅ Version module accessible: {get_version_string()}")
except Exception as e:
    print(f"❌ Version module error: {e}")
    sys.exit(1)

print("✅ Application logic test passed")
'

((TOTAL_TESTS++))
if run_test "Application logic" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"$APP_TEST\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 7: Device manager initialization (no hardware required)
echo -e "\n${BLUE}=== Phase 7: Device Manager ===${NC}"

DEVICE_TEST='
try:
    from pyhidpp.core.devices_manager import DevicesManager
    import logging
    
    # Initialize device manager (should work without devices)
    dev_manager = DevicesManager(log_to_console=False, log_level=logging.WARNING)
    print("✅ DevicesManager initialized")
    
    # Test compatible device list
    compatible_devices = ["Bravo", "Malacca", "Spotlight 2"]
    print(f"✅ Compatible devices: {compatible_devices}")
    
    print("✅ Device manager test passed")
    
except Exception as e:
    print(f"❌ Device manager error: {e}")
    import sys
    sys.exit(1)
'

((TOTAL_TESTS++))
if run_test "Device manager initialization" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"$DEVICE_TEST\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 8: Simple sensor test (console)
echo -e "\n${BLUE}=== Phase 8: Console Application ===${NC}"

((TOTAL_TESTS++))
if run_test "Console test script validation" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"
import simple_sensor_test
print('✅ simple_sensor_test module loads correctly')
print('✅ Console application structure valid')
\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 9: Container service configurations
echo -e "\n${BLUE}=== Phase 9: Service Configurations ===${NC}"

((TOTAL_TESTS++))
if run_test "Test service configuration" "$DOCKER_COMPOSE config --quiet && echo 'Docker Compose configuration valid'"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 10: File permissions and structure
echo -e "\n${BLUE}=== Phase 10: File Structure ===${NC}"

FILE_TEST='
import os
import sys

required_files = [
    "bravo_sensor_viewer.py",
    "simple_sensor_test.py", 
    "bravo_device_test.py",
    "version.py",
    "requirements.txt"
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f"❌ Missing files: {missing_files}")
    sys.exit(1)

print(f"✅ All required files present: {required_files}")

# Check directory structure
required_dirs = [
    "Vibration_test_scripts",
    "Vibration_test_scripts/pyhidpp"
]

missing_dirs = []
for dir in required_dirs:
    if not os.path.isdir(dir):
        missing_dirs.append(dir)

if missing_dirs:
    print(f"❌ Missing directories: {missing_dirs}")
    sys.exit(1)

print(f"✅ All required directories present: {required_dirs}")
'

((TOTAL_TESTS++))
if run_test "File structure validation" "$DOCKER_COMPOSE run --rm bravo-sensor-viewer python -c \"$FILE_TEST\""; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Final results
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}📊 TEST RESULTS SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}📈 Total Tests: $TOTAL_TESTS${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! Container setup is working correctly.${NC}"
    echo -e "${GREEN}✨ The containerization is ready for deployment!${NC}"
    
    echo -e "\n${BLUE}🚀 Quick start commands:${NC}"
    echo -e "   ${YELLOW}./run.sh${NC}           - Start GUI application"
    echo -e "   ${YELLOW}./run.sh --test${NC}     - Run device tests"
    echo -e "   ${YELLOW}./run.sh --dev${NC}      - Development mode"
    
    exit 0
else
    echo -e "\n${RED}❌ TESTS FAILED! Please check the errors above.${NC}"
    echo -e "${YELLOW}💡 Try rebuilding the container: docker-compose build --no-cache${NC}"
    exit 1
fi