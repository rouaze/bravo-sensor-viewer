# Bravo Sensor Viewer

A Python application for interfacing with Bravo sensors and visualizing sensor data, including vibration testing capabilities.

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