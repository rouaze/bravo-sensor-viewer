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

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/bravo-sensor-viewer.git
cd bravo-sensor-viewer
```

2. Install dependencies:
```bash
pip install -r requirements.txt  # Create this file with your dependencies
```

3. Run the application:
```bash
python bravo_sensor_viewer.py
```

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