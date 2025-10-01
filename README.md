# Bravo Sensor Viewer v2.0.0

🚀 **Professional Force Calibration Tool for Bravo, Malacca & Spotlight 2 Devices**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](version.py)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](requirements.txt)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 Overview

The Bravo Sensor Viewer is a professional-grade application for real-time force sensing and calibration with Logitech devices. It provides comprehensive sensor data visualization, threshold configuration, and force measurement capabilities.

### 🎯 Key Features

- **Real-time sensor visualization** with 3 synchronized plots
- **Force calibration** with customizable sensitivity settings
- **Dual threshold support** (L1/L2) via x19c0 and x9402 features
- **Multi-device compatibility**: Bravo, Malacca, Spotlight 2
- **Professional UI** with matplotlib integration
- **Containerized deployment** for easy setup
- **Cross-platform support** (Windows, Linux, macOS)

### 🔧 Device Features Used

- **Feature 0x9402**: Primary calibration data source via `read_cal_data(0)`
- **Feature 0x19c0**: Force sensing button thresholds (fallback)
- **HID++ protocol** for device communication

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Requirements**: Docker Desktop installed

#### Linux/macOS
```bash
git clone <your-repo-url>
cd bravo-sensor-viewer
./run.sh
```

#### Windows
```batch
git clone <your-repo-url>
cd bravo-sensor-viewer
run.bat
```

### Option 2: Local Development

**Requirements**: Python 3.7+, pip

```bash
git clone <your-repo-url>
cd bravo-sensor-viewer
./dev-setup.sh  # Linux/macOS
python bravo_sensor_viewer.py
```

---

## 🐳 Docker Deployment

### Prerequisites

- **Docker Desktop**: [Install Docker](https://docs.docker.com/get-docker/)
- **X11 Server** (Windows): Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)

### Available Run Modes

| Command | Description | Use Case |
|---------|-------------|----------|
| `./run.sh` | GUI application | Normal operation |
| `./run.sh --test` | Console tests only | Device verification |
| `./run.sh --dev` | Development mode | Code changes with hot reload |
| `./run.sh --console` | Console app without GUI | Headless environments |

### Docker Architecture

```yaml
# Three service configurations
services:
  bravo-sensor-viewer:    # Production GUI app
  bravo-sensor-test:      # Testing mode
  bravo-sensor-dev:       # Development with hot reload
```

### USB Device Access

The container automatically handles USB device access:
- **Linux**: Direct USB device mapping
- **Windows**: USB passthrough via Docker Desktop
- **macOS**: USB forwarding support

### GUI Display Setup

#### Linux
```bash
# X11 forwarding (automatic)
xhost +local:docker
export DISPLAY=:0
```

#### Windows
1. Install VcXsrv or Xming
2. Configure with "Disable access control"
3. Set DISPLAY=host.docker.internal:0.0

#### macOS
1. Install XQuartz: `brew install --cask xquartz`
2. Start XQuartz and allow network connections
3. Set DISPLAY=host.docker.internal:0

---

## 💻 Local Development Setup

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev python3-pip \
    libhidapi-dev libusb-1.0-0-dev \
    python3-pyqt5 qt5-default
```

#### macOS
```bash
brew install python3 hidapi qt5
pip3 install PyQt5
```

#### Windows
- Install Python 3.7+ from python.org
- Visual Studio Build Tools (for some packages)
- USB drivers automatically handled

### Development Setup

```bash
# Clone repository
git clone <your-repo-url>
cd bravo-sensor-viewer

# Run automated setup
./dev-setup.sh  # Linux/macOS
# Creates venv, installs deps, sets up tools

# Manual setup (Windows)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd Vibration_test_scripts/pyhidpp
pip install -e .
cd ..\..
```

### Development Tools

The setup includes:
- **Black**: Code formatting
- **Flake8**: Linting
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks
- **PyInstaller**: Executable building

```bash
# Code quality
black .                    # Format code
flake8 .                   # Check style
pytest tests/              # Run tests

# Build executable
pyinstaller bravo_sensor_viewer.spec
```

---

## 📁 Project Structure

```
bravo-sensor-viewer/
├── 📄 bravo_sensor_viewer.py      # Main GUI application
├── 🧪 simple_sensor_test.py       # Console test utility
├── 🔍 bravo_device_test.py        # Device discovery tool
├── 📦 version.py                   # Centralized version info
├── 🛠️ setup.py                    # Package configuration
├── 📋 requirements.txt             # Python dependencies
├── 🐳 Dockerfile                  # Container definition
├── 🎭 docker-compose.yml          # Multi-service orchestration
├── ⚙️ bravo_sensor_viewer.spec    # PyInstaller configuration
├── 🚀 run.sh / run.bat            # Quick start scripts
├── 🛠️ dev-setup.sh               # Development environment
├── 📖 README.md                   # This file
├── 📁 Vibration_test_scripts/     # Core libraries
│   ├── 🐍 pyhidpp/               # HID++ protocol library
│   └── 🔑 passwords_enc_mecha.ini.template
├── 📁 dist/                      # Built executables
├── 📁 build/                     # Build artifacts
├── 📁 logs/                      # Application logs
└── 📁 tests/                     # Test suite
```

---

## 🎮 Usage Guide

### Basic Operation

1. **Connect Device**: Plug in Bravo/Malacca/Spotlight 2
2. **Start Application**: Run via Docker or locally
3. **Auto-Connect**: App automatically discovers and connects
4. **Calibration**: Set calibration weight (default 150g)
5. **Start Monitoring**: Click "Start" for real-time data

### Interface Overview

- **Plot 1**: Touch ADC values with thresholds
- **Plot 2**: Baseline variations
- **Plot 3**: Preload values
- **Status Bar**: Real-time readings and force calculations
- **Sensitivity**: ADC/Newton conversion display

### Calibration Process

1. **Set Weight**: Enter calibration weight in grams
2. **Threshold Detection**: App reads L1/L2 from device
3. **Force Calculation**: `Force = ADC_Value / Sensitivity`
4. **Real-time Display**: Live force readings in Newtons/grams

---

## 🧪 Testing

### Quick Device Test
```bash
# Docker
./run.sh --test

# Local
python simple_sensor_test.py
```

### Full Test Suite
```bash
# Unit tests
pytest tests/

# Device discovery
python bravo_device_test.py

# GUI test (requires device)
python bravo_sensor_viewer.py
```

### Expected Output
```
🔍 Simple Sensor Test - Console Output v2.0.0
=====================================================
✅ Connected to Bravo
[001] ADC: 142, Baseline: 143, Preload: 21
[002] ADC: 145, Baseline: 143, Preload: 21
```

---

## 🔨 Building Executables

### Windows Executable
```bash
# In project root
pyinstaller --clean bravo_sensor_viewer.spec

# Output: dist/BravoSensorViewer_v2.0.0.exe
```

---

## 🚨 Troubleshooting

### Common Issues

#### ❌ "No device found"
- Verify USB connection
- Check device is powered on
- Try different USB port
- Run device test: `python bravo_device_test.py`

#### ❌ GUI not displaying (Docker)
- **Linux**: Run `xhost +local:docker`
- **Windows**: Start VcXsrv with "Disable access control"
- **macOS**: Ensure XQuartz allows network connections

#### ❌ Permission denied (USB)
- **Linux**: Add user to `plugdev` group: `sudo usermod -a -G plugdev $USER`
- **Docker**: Container runs as `plugdev` group member

#### ❌ Import errors
- Verify Python version: `python --version` (3.7+ required)
- Check virtual environment activation
- Reinstall requirements: `pip install -r requirements.txt`

### Debug Commands

```bash
# Check Docker setup
docker --version
docker compose version

# Test USB access
lsusb | grep -i logitech

# Check Python environment
python -c "import PyQt5, matplotlib, numpy; print('All imports OK')"

# Verify pyhidpp
python -c "from pyhidpp.core.devices_manager import DevicesManager; print('pyhidpp OK')"
```

---

## 📊 Version History

### v2.0.0 (2025-01-10)
- ✅ **Containerized deployment** with Docker support
- ✅ **Spotlight 2** device compatibility added
- ✅ **Version display** in UI and executable
- ✅ **Enhanced calibration** with sensitivity calculations
- ✅ **Cross-platform** easy-run scripts
- ✅ **Development environment** automation

### v1.x.x (Previous)
- Basic sensor visualization
- Bravo/Malacca support
- Manual setup required

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Install** dev environment: `./dev-setup.sh`
4. **Make** changes and test thoroughly
5. **Format** code: `black . && flake8 .`
6. **Test**: `pytest tests/`
7. **Commit**: `git commit -m 'Add amazing feature'`
8. **Push**: `git push origin feature/amazing-feature`
9. **PR**: Create Pull Request

### Code Style
- **Black** formatting (line length 120)
- **Flake8** linting
- **Type hints** encouraged
- **Docstrings** for public functions

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Pierre Rouaze**
- 🔧 Professional Force Calibration Tools
- 📧 Contact via GitHub issues

---

## 🙏 Acknowledgments

- **pyhidpp library** for HID++ protocol implementation
- **Qt/PyQt5** for professional GUI framework
- **Matplotlib** for real-time plotting capabilities
- **Docker** for containerization support

---

**🚀 Ready to start? Run `./run.sh` or `run.bat` and connect your device!**

## Features

- **Bravo Device Testing**: Interface with Bravo sensor devices
- **Live Sensor Viewing**: Real-time sensor data visualization  
- **Vibration Analysis**: Tools for vibration testing and waveform analysis
- **HID++ Communication**: Low-level device communication using HID++ protocol

## Project Structure

```
├── bravo_device_test.py          # Device testing functionality
├── bravo_sensor_viewer.py        # Main sensor viewer application
├── live_viewer.py                # Real-time data visualization
├── simple_sensor_test.py         # Basic sensor testing
├── Vibration_test_scripts/       # Vibration analysis tools
│   ├── malacca_vibration_test_waveforms.py
│   └── x9401.py
├── x19c0FeatureDoc.pdf          # Feature documentation
└── x9402FeatureDoc.pdf          # Feature documentation
```

## Requirements

- Python 3.7 or higher
- Required Python packages (see requirements.txt):
  - PyQt5 (GUI framework)
  - matplotlib (plotting and visualization)
  - numpy (numerical computations)
  - pytest (testing framework)

## Usage

### Basic Sensor Testing
```bash
python simple_sensor_test.py
```

### Bravo Device Testing  
```bash
python bravo_device_test.py
```

### Live Sensor Viewing
```bash
python live_viewer.py
```

### Vibration Testing
```bash
python Vibration_test_scripts/malacca_vibration_test_waveforms.py
```

## Installation

### Prerequisites
- **Python 3.7+** (tested with Python 3.8+)
- **Windows/Linux/macOS** with USB HID access
- **Bravo or Malacca device** with compatible dongle

### Step 1: Clone and Setup
```bash
git clone https://github.com/rouaze/bravo-sensor-viewer.git
cd bravo-sensor-viewer
pip install -r requirements.txt
```

### Step 2: Device Authentication Setup
**⚠️ IMPORTANT**: You need a password file for device authentication.

Create `Vibration_test_scripts/passwords_enc_mecha.ini` with your device passwords:
```ini
# Device password configuration
# Contact your device administrator for encrypted passwords
[PASSWORDS]
# Add your device-specific encrypted passwords here
# Format: DEVICE_ID=ENCRYPTED_PASSWORD
```

### Step 3: System Requirements
- **Windows**: No additional drivers needed (uses built-in HID)
- **Linux**: May need `sudo` access or udev rules for USB devices
- **macOS**: May need permission for USB device access

### Step 4: Run Application
```bash
# Main sensor viewer (GUI)
python bravo_sensor_viewer.py

# Simple console test
python simple_sensor_test.py

# Live plotting
python live_viewer.py

# Device testing
python bravo_device_test.py
```

## Troubleshooting

### Common Issues

#### "No device found" Error
- **Check hardware**: Ensure Bravo/Malacca device is connected via USB dongle
- **USB permissions**: On Linux, you may need udev rules or sudo access
- **Driver issues**: Try a different USB port or restart the application

#### "Password not present" Error
- **Missing password file**: Copy `passwords_enc_mecha.ini.template` to `passwords_enc_mecha.ini`
- **Invalid passwords**: Contact device administrator for correct encrypted passwords
- **File location**: Ensure password file is in `Vibration_test_scripts/` directory

#### "Sensor not responding" Error
- **Device unlock failed**: Check password file configuration
- **Communication timeout**: Try disconnecting and reconnecting the device
- **Feature unavailable**: Device may not support required HID++ features (0x9402, 0x19c0)

#### ImportError or Module Not Found
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Python version**: Ensure Python 3.7+ is installed
- **Virtual environment**: Consider using a virtual environment

### System-Specific Notes

#### Windows
- Uses built-in HID drivers
- No additional setup required

#### Linux
- May require udev rules for non-root access:
```bash
sudo echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", MODE="0666"' > /etc/udev/rules.d/99-logitech-hidpp.rules
sudo udevadm control --reload-rules
```

#### macOS
- May prompt for USB device access permissions
- Grant permissions in System Preferences → Privacy & Security

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

[Add your license information here]

## Contact

[Add your contact information here]