# 🧪 Testing Guide for Bravo Sensor Viewer v2.0.0

This guide provides comprehensive instructions for testing the containerized setup and verifying that everything works correctly after a git clone.

## 📋 Quick Test Commands

### With Docker (Recommended)
```bash
# Linux/macOS
./test-container.sh

# Windows
test-container.bat
```

### Without Docker (Local Testing)
```bash
# Linux/macOS
./dev-setup.sh && python -m pytest tests/

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "from version import __version__; print(f'Version: {__version__}')"
```

---

## 🐳 Docker Container Tests

### Prerequisites
- Docker Desktop installed and running
- Git repository cloned
- Command line access

### Test Categories

#### 1. **Container Build Test**
```bash
# Test that container builds without errors
docker compose build --no-cache

# Expected output: "Successfully built" message
# Build time: ~2-5 minutes depending on system
```

#### 2. **Python Environment Test**
```bash
# Verify Python and dependencies
docker compose run --rm bravo-sensor-viewer python --version
# Expected: Python 3.11.x

docker compose run --rm bravo-sensor-viewer python -c "
import PyQt5, matplotlib, numpy
from pyhidpp.core.devices_manager import DevicesManager
print('✅ All core dependencies available')
"
```

#### 3. **Version Integration Test**
```bash
# Test version information works correctly
docker compose run --rm bravo-sensor-viewer python -c "
from version import __version__, __author__, get_version_string
print(f'Version: {__version__}')
print(f'Author: {__author__}')
print(f'Version String: {get_version_string()}')
assert __version__ == '2.0.0'
assert __author__ == 'Pierre Rouaze'
print('✅ Version information correct')
"
```

#### 4. **Device Compatibility Test**
```bash
# Test device manager initialization (no hardware required)
docker compose run --rm bravo-sensor-viewer python -c "
from pyhidpp.core.devices_manager import DevicesManager
import logging

dev_manager = DevicesManager(log_to_console=False, log_level=logging.WARNING)
compatible = ['Bravo', 'Malacca', 'Spotlight 2']
print(f'✅ Compatible devices: {compatible}')
print('✅ Device manager initializes correctly')
"
```

#### 5. **Feature Support Test**
```bash
# Test feature classes load correctly
docker compose run --rm bravo-sensor-viewer python -c "
from pyhidpp.features.x9402 import X9402
from pyhidpp.features.x19c0 import X19C0
print('✅ Feature 0x9402 (calibration) available')
print('✅ Feature 0x19c0 (force sensing) available')
print('✅ All required features supported')
"
```

#### 6. **GUI Framework Test** (Headless)
```bash
# Test GUI components without display
docker compose run --rm bravo-sensor-viewer python -c "
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt

# Test plotting functionality
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.savefig('/tmp/test.png')
print('✅ Matplotlib plotting works')

# Test version display
from version import get_version_string
title = f'Bravo Sensor Viewer {get_version_string()}'
print(f'✅ GUI title: {title}')
"
```

---

## 🖥️ GUI and USB Testing

### X11 Display Testing (Linux)

1. **Setup X11 forwarding:**
```bash
# Allow Docker to access X11
xhost +local:docker
export DISPLAY=:0
```

2. **Test GUI launch:**
```bash
# Should open GUI window (requires X11)
./run.sh

# Test output should show:
# - Window opens with "Bravo Sensor Viewer v2.0.0" title
# - Version info displayed in UI
# - Three empty plots ready for data
```

### Windows X11 Testing

1. **Install X11 server:**
   - Download [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
   - Configure with "Disable access control" option

2. **Test GUI launch:**
```batch
# Should open GUI window
run.bat

# Expected behavior:
# - X11 server starts automatically
# - GUI window appears
# - Version v2.0.0 visible in title and UI
```

### USB Device Testing

**With Physical Device:**
```bash
# Connect Bravo/Malacca/Spotlight 2 device
./run.sh --test

# Expected output:
# ✅ Connected to [Device Name]
# [001] ADC: xxx, Baseline: xxx, Preload: xx
# [002] ADC: xxx, Baseline: xxx, Preload: xx
```

**Without Physical Device:**
```bash
# Should show connection attempts
./run.sh --test

# Expected output:
# ❌ Could not connect to any compatible device
# (This is normal without hardware)
```

---

## 🔧 Local Development Testing

### Manual Environment Setup Test

1. **Create virtual environment:**
```bash
python -m venv test_env
source test_env/bin/activate  # Linux/macOS
# OR
test_env\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
cd Vibration_test_scripts/pyhidpp
pip install -e .
cd ../..
```

3. **Test core functionality:**
```bash
# Test version module
python -c "
from version import __version__, __author__
print(f'Version: {__version__}')
print(f'Author: {__author__}')
assert __version__ == '2.0.0'
print('✅ Version test passed')
"

# Test device manager
python -c "
from pyhidpp.core.devices_manager import DevicesManager
print('✅ Device manager import successful')
"

# Test GUI framework
python -c "
import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
print('✅ PyQt5 GUI framework working')
app.quit()
"
```

### Automated Development Test

```bash
# Run automated setup
./dev-setup.sh

# Expected output:
# ✅ Python X.X.X detected
# ✅ Virtual environment created
# ✅ Requirements installed
# ✅ Development tools installed
# 🎉 Development environment setup complete!
```

---

## 🏗️ Executable Testing

### PyInstaller Build Test

1. **Build executable:**
```bash
# Clean build
pyinstaller --clean bravo_sensor_viewer.spec

# Expected output:
# - Build completes without errors
# - Creates dist/BravoSensorViewer_v2.0.0.exe
# - File size ~50-100MB
```

2. **Test executable properties:**
```bash
# Windows: Check file properties
# Should show:
# - Version: 2.0.0
# - Description: Professional Force Calibration Tool
# - Company: Pierre Rouaze
```

3. **Run executable test:**
```bash
# Should launch without Python installed
./dist/BravoSensorViewer_v2.0.0.exe

# Expected:
# - GUI opens immediately
# - Version v2.0.0 visible
# - No console errors
```

---

## 📊 Expected Test Results

### ✅ **Success Indicators**

| Test | Expected Result |
|------|----------------|
| Container Build | "Successfully built" message |
| Python Version | "Python 3.11.x" output |
| Core Imports | All imports succeed without errors |
| Version Info | Shows "2.0.0", "Pierre Rouaze" |
| GUI Framework | PyQt5 initializes correctly |
| Device Manager | Creates without exceptions |
| Feature Classes | x9402 and x19c0 load successfully |
| Executable Build | Creates versioned .exe file |

### ❌ **Failure Scenarios & Solutions**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Docker not found" | Docker not installed | Install Docker Desktop |
| "Permission denied" | Linux USB access | Add user to plugdev group |
| "GUI not showing" | X11 not configured | Setup VcXsrv/XQuartz |
| "Import errors" | Missing dependencies | Run `pip install -r requirements.txt` |
| "Build fails" | Missing system libs | Install dev packages (`libhidapi-dev`) |

---

## 🚀 Complete Integration Test

**Full workflow test (with device):**

1. **Clone and test:**
```bash
git clone <your-repo>
cd bravo-sensor-viewer
./test-container.sh
```

2. **Expected complete output:**
```
🧪 Bravo Sensor Viewer v2.0.0 - Container Testing
=======================================================

=== Phase 1: Prerequisites ===
✅ PASS: Docker availability

=== Phase 2: Container Build ===  
✅ PASS: Container build

=== Phase 3: Python Environment ===
✅ PASS: Python version check

=== Phase 4: Core Dependencies ===
✅ PASS: Core imports

=== Phase 5: Version Information ===
✅ PASS: Version information

=== Phase 6: Application Logic ===
✅ PASS: Application logic

=== Phase 7: Device Manager ===
✅ PASS: Device manager initialization

=== Phase 8: Console Application ===
✅ PASS: Console test script validation

=== Phase 9: Service Configurations ===
✅ PASS: Test service configuration

=== Phase 10: File Structure ===
✅ PASS: File structure validation

========================================
📊 TEST RESULTS SUMMARY
========================================
✅ Tests Passed: 10
❌ Tests Failed: 0
📈 Total Tests: 10

🎉 ALL TESTS PASSED! Container setup is working correctly.
✨ The containerization is ready for deployment!
```

3. **Run application:**
```bash
./run.sh
# GUI opens with device auto-detection
```

---

## 💡 Testing Tips

- **Run tests incrementally** - Start with container build, then move to functionality
- **Check logs** - Use `docker compose logs` for debugging
- **Test without device** first - Verify software stack before hardware
- **Use test modes** - `./run.sh --test` for device-specific testing
- **Verify versions** - Ensure v2.0.0 appears in all components

---

**✅ When all tests pass, the containerization is working perfectly and ready for GitHub deployment!**