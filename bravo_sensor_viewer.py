#!/usr/bin/env python3
"""
Updated sensor viewer for Bravo device with proper initialization order
"""

import sys
import os

# Import version information from centralized version file
try:
    from version import __version__, __build_date__, get_version_string
except ImportError:
    # Fallback if version.py is not available
    __version__ = "2.0.0"
    __build_date__ = "2025-01-10"
    get_version_string = lambda: f"v{__version__} ({__build_date__})"
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, QGroupBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from collections import deque
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.security import SecurityManager
from pyhidpp.features.x9402 import X9402
from pyhidpp.features.x19c0 import X19C0
import logging
import time

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=10, dpi=100):
        # Create figure with 3 subplots for comprehensive x9402 data display
        self.fig, self.axs = plt.subplots(3, 1, figsize=(width, height), dpi=dpi)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.x_data_arr = []
        self.y_data_arr = []
        self.lines = []
        self.max_points = 200
        
        # Enhanced titles and labels for x9402 feature data
        self.axs[0].set_title('HID++ Feature 0x9402: Touch ADC Values', fontsize=10, pad=15)
        self.axs[0].set_ylabel('ADC Value')
        self.axs[0].grid(True, alpha=0.3)
        
        self.axs[1].set_title('HID++ Feature 0x9402: Baseline Variations', fontsize=10, pad=15)
        self.axs[1].set_ylabel('Baseline')
        self.axs[1].grid(True, alpha=0.3)
        
        self.axs[2].set_title('HID++ Feature 0x9402: Preload Values', fontsize=10, pad=15)
        self.axs[2].set_ylabel('Preload')
        self.axs[2].set_xlabel('Sample Number')
        self.axs[2].grid(True, alpha=0.3)

        # Initialize each subplot
        for i, ax in enumerate(self.axs):
            ax.set_xlim(0, 100)
            ax.set_ylim(-100, 600)
            self.x_data_arr.append(deque(maxlen=self.max_points))
            self.y_data_arr.append(deque(maxlen=self.max_points))
            line, = ax.plot([], [], '-', linewidth=1.5)
            self.lines.append(line)

        # Enhanced layout with proper spacing to prevent overlap
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.08, hspace=0.4)

class BravoSensorWindow(QMainWindow):
    def __init__(self):
        super(BravoSensorWindow, self).__init__()
        self.setWindowTitle(f"SPOTLIGHT 2 Sensor Viewer v{__version__} - Professional Force Calibration Tool")
        self.resize(1200, 800)  # Much larger default size for professional layout
        
        # Set minimum size to prevent excessive squishing
        self.setMinimumSize(1000, 600)

        # Initialize variables
        self.mouse = None
        self.sensing_feature = None
        self.force_sensing_feature = None
        self.counter = 0
        self.sensor_available = False
        
        # Threshold variables
        self.l1_threshold = None
        self.l2_threshold = None
        self.threshold_lines = []
        self.threshold_message = "No thresholds available"
        
        # Calibration variables
        self.calibration_weight_grams = 200.0  # Default 200 grams
        self.sensitivity_adc_per_n = None

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add matplotlib canvas
        self.canvas = MatplotlibCanvas(self)
        layout.addWidget(self.canvas)
        
        # Add matplotlib toolbar
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)
        
        # Add version info and control buttons
        version_layout = QHBoxLayout()
        version_label = QLabel(f"Version {__version__} ({__build_date__})")
        version_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 10px; }")
        version_layout.addStretch()
        version_layout.addWidget(version_label)
        layout.addLayout(version_layout)
        
        # Add control buttons
        button_layout = QHBoxLayout()
        self.status_label = QLabel("Initializing...")
        
        # Make status label text bigger and more readable
        status_font = QFont()
        status_font.setPointSize(14)  # Larger font size
        status_font.setBold(True)     # Make it bold
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("QLabel { color: #2c3e50; padding: 5px; }")
        
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")
        self.connect_button = QPushButton("Reconnect")
        
        self.start_button.clicked.connect(self.start_data_acquisition)
        self.stop_button.clicked.connect(self.stop_data_acquisition)
        self.clear_button.clicked.connect(self.clear_data)
        self.connect_button.clicked.connect(self.connect_device)
        
        button_layout.addWidget(self.status_label)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Add calibration group box
        calibration_group = QGroupBox("Sensitivity")
        calibration_layout = QHBoxLayout(calibration_group)
        
        # Calibration weight input
        calibration_layout.addWidget(QLabel("Calibration Weight:"))
        self.weight_input = QLineEdit("200.0")
        self.weight_input.setMaximumWidth(80)
        self.weight_input.setToolTip("Calibration weight in grams (default 200g)")
        self.weight_input.textChanged.connect(self.update_calibration)
        calibration_layout.addWidget(self.weight_input)
        calibration_layout.addWidget(QLabel("g"))
        
        # Add some spacing
        calibration_layout.addWidget(QLabel("    "))
        
        # Sensitivity display
        calibration_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_label = QLabel("Not calculated")
        self.sensitivity_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        self.sensitivity_label.setToolTip("ADC counts per Newton (based on L1 threshold)")
        calibration_layout.addWidget(self.sensitivity_label)
        
        # Add stretch to right-align
        calibration_layout.addStretch()
        
        layout.addWidget(calibration_group)
        
        # Setup timer for data updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.update_interval = 100  # milliseconds
        
        # Initialize UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def disable_ui_during_connection(self):
        """Disable all interactive UI elements during connection/reconnection"""
        self.connect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.weight_input.setEnabled(False)
        
        # Update button text to show it's connecting
        self.connect_button.setText("Connecting...")

    def enable_ui_after_connection(self, sensor_available=False):
        """Re-enable UI elements after connection attempt (success or failure)"""
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Reconnect")
        self.clear_button.setEnabled(True)
        self.weight_input.setEnabled(True)
        
        # Enable start/stop buttons based on sensor availability
        if sensor_available:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def update_calibration(self):
        """Update sensitivity calculation based on calibration weight and L1 threshold"""
        try:
            # Parse calibration weight
            weight_text = self.weight_input.text()
            self.calibration_weight_grams = float(weight_text)
            
            # Calculate if we have L1 threshold
            if self.l1_threshold is not None and self.l1_threshold > 0:
                # Convert grams to Newtons: F = mg, where g = 9.81 m/s²
                force_newtons = (self.calibration_weight_grams / 1000.0) * 9.81
                
                # Calculate sensitivity: ADC counts per Newton
                self.sensitivity_adc_per_n = self.l1_threshold / force_newtons
                
                # Update display
                self.sensitivity_label.setText(f"{self.sensitivity_adc_per_n:.1f} ADC/N")
                self.sensitivity_label.setToolTip(f"Sensitivity: {self.sensitivity_adc_per_n:.1f} ADC counts per Newton\n"
                                                f"Based on L1={self.l1_threshold} ADC @ {self.calibration_weight_grams}g ({force_newtons:.3f}N)")
                
                print(f"Sensitivity calculated: {self.sensitivity_adc_per_n:.1f} ADC/N ({self.calibration_weight_grams}g = {force_newtons:.3f}N)")
            else:
                self.sensitivity_adc_per_n = None
                self.sensitivity_label.setText("L1 threshold needed")
                self.sensitivity_label.setToolTip("Connect device and get L1 threshold to calculate sensitivity")
                
        except ValueError:
            self.sensitivity_label.setText("Invalid weight")
            self.sensitivity_label.setToolTip("Enter a valid weight in grams")
        except Exception as e:
            self.sensitivity_label.setText("Calculation error")
            self.sensitivity_label.setToolTip(f"Error: {e}")

    def get_thresholds(self):
        """Get L1 and L2 thresholds using x19c0 with fallback to x9402
        
        Returns:
            tuple: (l1_threshold, l2_threshold, message) or (None, None, error_message)
        """
        print("Getting threshold values...")
        
        # Reset threshold values
        l1_threshold = None
        l2_threshold = None
        message = "No thresholds available"
        
        # First attempt: Try x19c0 Force Sensing Button feature
        try:
            if self.force_sensing_feature:
                print("  Trying x19c0 Force Sensing Button feature...")
                threshold_data = self.force_sensing_feature.get_button_config(0)  # Button ID 0
                
                if threshold_data is not None:
                    l1_threshold, l2_threshold = threshold_data
                    print(f"  x19c0 thresholds found - L1: {l1_threshold}, L2: {l2_threshold}")
                    
                    # Build threshold message
                    if l2_threshold > 0:
                        message = f"L1: {l1_threshold} ADC, L2: {l2_threshold} ADC"
                    else:
                        message = f"L1: {l1_threshold} ADC"
                    
                    # Update sensitivity calculation after getting thresholds
                    self.l1_threshold = l1_threshold
                    self.l2_threshold = l2_threshold
                    self.update_calibration()
                    return (l1_threshold, l2_threshold, message)
                else:
                    print("  x19c0 getButtonConfig returned None")
            else:
                print("  x19c0 force sensing feature not available")
        except Exception as e:
            print(f"  x19c0 threshold reading failed: {e}")
        
        # Second attempt: Fallback to x9402 nominal threshold
        try:
            if self.sensing_feature:
                print("  Trying x9402 calibration fallback...")
                cal_data = self.sensing_feature.read_cal_data(0)
                
                if cal_data is not None:
                    nom_th, low_th, high_th = cal_data
                    print(f"  x9402 calibration - Nominal: {nom_th}, Low: {low_th}, High: {high_th}")
                    
                    # Use nominal as L1, no L2
                    if 0 < nom_th < 1000:  # Sanity check
                        l1_threshold = nom_th
                        l2_threshold = 0  # No L2 from x9402
                        message = f"L1: {nom_th} ADC (from x9402 nominal)"
                        print(f"  Using x9402 nominal threshold as L1: {nom_th}")
                        
                        # Update sensitivity calculation after getting thresholds
                        self.l1_threshold = l1_threshold
                        self.l2_threshold = l2_threshold
                        self.update_calibration()
                        return (l1_threshold, l2_threshold, message)
                    else:
                        print(f"  x9402 nominal threshold out of range: {nom_th}")
                else:
                    print("  x9402 read_cal_data returned None")
            else:
                print("  x9402 sensing feature not available")
        except Exception as e:
            print(f"  x9402 fallback failed: {e}")
        
        # No thresholds available - clear sensitivity calculation
        print("  No threshold sources available")
        self.l1_threshold = None
        self.l2_threshold = None
        self.update_calibration()
        return (None, None, "No thresholds available")

    def connect_device(self):
        """Connect and initialize device with OPTIMIZED speed"""
        import time  # Import at the beginning to avoid scoping issues
        start_time = time.time()
        self.status_label.setText("Connecting...")
        
        # Stop any running timers first
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        # ENHANCED CLEANUP: Handle dongle unplug crashes and thread recovery
        if hasattr(self, 'mouse') and self.mouse:
            try:
                print(" Performing complete disconnect and dongle reset...")
                
                # CRITICAL: Handle crashed HID threads from dongle unplug
                try:
                    print("   Stopping communication threads...")
                    self.mouse.stop_listener_thread()
                    self.mouse.stop_commander_thread()
                    print("     Threads stopped successfully")
                except Exception as thread_error:
                    print(f"     Thread stop error (expected after unplug): {thread_error}")
                
                # Force disconnect even if threads crashed
                try:
                    print("   Forcing device disconnect...")
                    self.mouse.disconnect()
                    print("     Device disconnected")
                except Exception as disconnect_error:
                    print(f"     Disconnect error (expected after unplug): {disconnect_error}")
                
                print("   Cleanup completed (threads and device)")
            except Exception as cleanup_error:
                print(f"   General cleanup error: {cleanup_error}")
            finally:
                # CRITICAL: Always clear reference regardless of errors
                self.mouse = None
            
        self.sensor_available = False
        self.sensing_feature = None
        
        # OPTIMIZED USB RECOVERY: Reduced delay for faster connection
        print(" Waiting for USB subsystem recovery...")
        import time
        
        # Reduced recovery time - most devices don't need 5 seconds
        for i in range(2):
            print(f"  Recovery phase {i+1}/2...")
            time.sleep(0.5)  # 1 second total for USB subsystem recovery
        
        print("   USB recovery completed")
        
        try:
            # Step 1: Create FRESH DevicesManager (rescans USB devices)
            print(" Creating fresh device manager (USB rescan)...")
            dev_manager = DevicesManager(log_to_console=False, log_level=logging.WARNING)
            print("   USB device scan completed")
            compatible_devices = ["Bravo", "Malacca", "Spotlight 2", "SPOTLIGHT 2"]
            
            connection_attempts = 0
            max_attempts = 2  # Reduced from 3 to 2 attempts
            
            while connection_attempts < max_attempts:
                connection_attempts += 1
                print(f"Connection attempt {connection_attempts}/{max_attempts}")
                
                for device_name in compatible_devices:
                    self.mouse = dev_manager.connect_with_name(device_name)
                    if self.mouse:
                        print(f" Connected to: {device_name}")
                        break
                
                if self.mouse:
                    break
                    
                if connection_attempts < max_attempts:
                    print("Connection failed, waiting 1 second before retry...")
                    import time
                    time.sleep(1)  # Reduced from 2 seconds to 1 second
            
            if not self.mouse:
                self.status_label.setText(" No device found after retries")
                self.enable_ui_after_connection(sensor_available=False)
                return False
            
            # Step 2: OPTIMIZED Security unlock with faster retry
            unlock_attempts = 0
            max_unlock_attempts = 2
            
            while unlock_attempts < max_unlock_attempts:
                unlock_attempts += 1
                print(f"Unlock attempt {unlock_attempts}/{max_unlock_attempts}")
                
                try:
                    # Reduced diagnostic output for faster execution
                    password_file_path = get_resource_path('Vibration_test_scripts/passwords_enc_mecha.ini')
                    if unlock_attempts == 1:  # Only print path on first attempt
                        print(f" Using password file: {password_file_path}")

                    sm = SecurityManager(self.mouse, password_file_path)
                    unlock_result = sm.unlock_device()
                    
                    # Step 3: Enumerate all features (after unlock) with verification
                    self.mouse.enumerate_all()
                    
                    # Reduced settling time for faster connection
                    import time
                    time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
                    
                    # Verify feature count - should be 37 for properly unlocked device
                    if hasattr(self.mouse, 'device_info') and hasattr(self.mouse.device_info, 'features'):
                        feature_count = len(self.mouse.device_info.features)
                        print(f"Features enumerated: {feature_count}")
                        
                        if feature_count >= 30:  # Should have ~37, but accept >= 30
                            print(f" Full feature set available ({feature_count} features)")
                            # Reduced additional settling time
                            time.sleep(0.3)  # Reduced from 1 second to 0.3 seconds
                            break
                        else:
                            print(f" Limited features ({feature_count}) - retrying...")
                            if unlock_attempts < max_unlock_attempts:
                                time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
                                continue
                    
                except Exception as unlock_error:
                    print(f"Unlock attempt {unlock_attempts} failed: {unlock_error}")
                    if unlock_attempts >= max_unlock_attempts:
                        raise unlock_error
            
            # Step 4: Display device info
            if hasattr(self.mouse, 'device_info'):
                info = self.mouse.device_info
                print(f"Device: {getattr(info, 'product_name', 'Unknown')}")
                print(f"PID: 0x{getattr(info, 'pid', 0):04X}")
                feature_count = len(info.features) if hasattr(info, 'features') else 0
                print(f"Available Features: {feature_count}")
                
                # Check for sensor feature (x9402)
                if hasattr(info, 'features') and 0x9402 in info.features:
                    print(f" Sensor feature 0x9402 found at index {info.features[0x9402].idx}")
                    self.sensor_available = True
                else:
                    print(" Sensor feature 0x9402 not available")
                    self.sensor_available = False
                
                # Check for force sensing button feature (x19c0)
                force_sensing_available = False
                if hasattr(info, 'features') and 0x19c0 in info.features:
                    print(f" Force sensing feature 0x19c0 found at index {info.features[0x19c0].idx}")
                    force_sensing_available = True
                else:
                    print(" Force sensing feature 0x19c0 not available")
                
                # If we don't have enough features, the device might need more time
                if not self.sensor_available and feature_count < 10:
                    print(f" Only {feature_count} features available - device may need more initialization time")
                    self.status_label.setText(" Device initialization incomplete - try Reconnect")
                    self.enable_ui_after_connection(sensor_available=False)
                    return False
            
            # Step 5: Initialize sensor and force sensing features
            sensor_init_success = False
            
            # Initialize x9402 sensor feature if available
            if self.sensor_available:
                print("Initializing x9402 sensor feature with retry logic...")
                
                # Clear any existing sensor feature reference
                self.sensing_feature = None
                time.sleep(0.5)  # Allow cleanup
                
                # OPTIMIZED sensor initialization with reduced retries and delays
                for sensor_attempt in range(2):  # Reduced from 3 to 2 attempts
                    try:
                        print(f"x9402 initialization attempt {sensor_attempt + 1}/2...")
                        self.sensing_feature = X9402(self.mouse)
                        
                        # Reduced initialization delay
                        time.sleep(0.1)  # Reduced from 0.2 to 0.1 seconds
                        
                        # Single test reading for faster initialization
                        print(f"  Testing x9402 reading...")
                        test_result = self.sensing_feature.read_measurement(0)
                        if test_result is not None:
                            print(f"   x9402 test successful")
                            
                            # Quick validation without extensive logging
                            try:
                                if isinstance(test_result, (list, tuple)) and len(test_result) >= 3:
                                    val, bl, pl = test_result
                                    if sensor_attempt == 0:  # Only log details on first attempt
                                        print(f"   Values - Val: {val}, BL: {bl}, PL: {pl}")
                            except Exception:
                                pass  # Don't let unpacking errors stop initialization
                            
                            sensor_init_success = True
                            print(" x9402 sensor feature initialized successfully")
                            break
                        else:
                            print(f"   x9402 test returned None")
                            if sensor_attempt < 1:  # Only sleep between attempts, not after last
                                time.sleep(0.3)  # Reduced from 0.5 seconds
                    
                    except Exception as sensor_e:
                        print(f"   x9402 initialization attempt {sensor_attempt + 1} failed: {sensor_e}")
                        self.sensing_feature = None
                        if sensor_attempt < 1:  # Only sleep between attempts, not after last
                            time.sleep(0.3)  # Reduced from 1 second
                
                if not sensor_init_success:
                    print(" x9402 sensor initialization failed after all attempts")
            else:
                print(" x9402 sensor feature not available")
            
            # Initialize x19c0 force sensing feature if available
            force_init_success = False
            if force_sensing_available:
                print("Initializing x19c0 force sensing feature...")
                
                # OPTIMIZED force sensing initialization
                self.force_sensing_feature = None
                time.sleep(0.1)  # Reduced from 0.2 seconds
                
                try:
                    self.force_sensing_feature = X19C0(self.mouse)
                    
                    # Quick capability test
                    capabilities = self.force_sensing_feature.get_capabilities()
                    if capabilities is not None:
                        print(f"   x19c0 capabilities: {capabilities} buttons")
                        force_init_success = True
                        
                        # Optional threshold reading - don't fail if it doesn't work
                        try:
                            thresholds = self.force_sensing_feature.get_button_config(0)
                            if thresholds is not None:
                                l1, l2 = thresholds
                                print(f"   x19c0 thresholds: L1={l1}, L2={l2}")
                        except Exception:
                            print("   x19c0 threshold reading failed (will retry later)")
                    else:
                        print("   x19c0 capabilities reading failed")
                        
                except Exception as force_e:
                    print(f"   x19c0 initialization failed: {force_e}")
                    self.force_sensing_feature = None
                    
                if force_init_success:
                    print(" x19c0 force sensing feature initialized successfully")
                else:
                    print(" x19c0 force sensing feature initialization failed")
            else:
                print(" x19c0 force sensing feature not available")
            
            # Set status based on available features
            connection_time = time.time() - start_time
            if sensor_init_success:
                self.status_label.setText(f" Ready - Sensor Available (Connected in {connection_time:.1f}s)")
                self.enable_ui_after_connection(sensor_available=True)
            elif force_init_success:
                self.status_label.setText(f" Ready - Force Sensing Available (Connected in {connection_time:.1f}s)")
                self.enable_ui_after_connection(sensor_available=True)
            else:
                self.status_label.setText(f" Device connected, limited functionality (Connected in {connection_time:.1f}s)")
                self.enable_ui_after_connection(sensor_available=False)
            
            print(f"OPTIMIZED CONNECTION COMPLETED in {connection_time:.1f} seconds")
            return True
            
        except Exception as e:
            print(f" Connection error: {e}")
            self.status_label.setText(f" Error: {e}")
            self.enable_ui_after_connection(sensor_available=False)
            if hasattr(self, 'mouse') and self.mouse:
                try:
                    self.mouse.disconnect()
                except:
                    pass
            self.mouse = None
            return False

    def start_data_acquisition(self):
        if not self.sensor_available or not self.sensing_feature:
            self.status_label.setText(" No sensor available")
            return
            
        try:
            # Test initial reading and setup calibration
            print("Starting data acquisition...")
            measurement_result = self.sensing_feature.read_measurement(0)
            print(f"Initial measurement result: {measurement_result}")
            
            if measurement_result is None:
                print(" Initial sensor reading returned None")
                self.status_label.setText(" Sensor not responding")
                return
            
            # Handle different result formats
            try:
                if isinstance(measurement_result, (list, tuple)) and len(measurement_result) >= 3:
                    new_measurement, bl, pl = measurement_result
                    print(f"Initial reading - Val: {new_measurement}, BL: {bl}, PL: {pl}")
                else:
                    # Handle single value or unexpected format
                    print(f"Unexpected measurement format: {measurement_result}")
                    new_measurement = measurement_result if isinstance(measurement_result, (int, float)) else 0
                    bl = 0
                    pl = 0
                    print(f"Using fallback values - Val: {new_measurement}, BL: {bl}, PL: {pl}")
            except Exception as e:
                print(f"Error processing initial measurement: {e}")
                new_measurement, bl, pl = 0, 0, 0
            
            # Setup plot limits based on sensor data range (-16 to 510 observed)
            print(f"Setting up plots for comprehensive x9402 feature data...")
            
            # ADC plot: use range that covers observed sensor values
            self.canvas.axs[0].set_ylim([-50, 600])  # Covers -16 to 510+ range
            
            # Baseline plot: focus on baseline variations
            self.canvas.axs[1].set_ylim([bl-20, bl+20])  # Tighter range for baseline ~143
            
            # Preload plot: typical preload range
            self.canvas.axs[2].set_ylim([pl-10, pl+10])  # Range around preload value
            
            # Get threshold data using new system (x19c0 with x9402 fallback)
            self.l1_threshold, self.l2_threshold, self.threshold_message = self.get_thresholds()
            
            # Clear any existing threshold lines
            for line in self.threshold_lines:
                line.remove()
            self.threshold_lines.clear()
            
            # Add threshold lines and labels to ADC plot
            if self.l1_threshold is not None:
                print(f"Adding threshold lines: {self.threshold_message}")
                
                # Add L1 threshold line
                l1_line = self.canvas.axs[0].axhline(y=self.l1_threshold, color='red',
                                                   linestyle='--', alpha=0.8, linewidth=2,
                                                   label=f'L1: {self.l1_threshold} ADC')
                self.threshold_lines.append(l1_line)
                
                # Add L2 threshold line if available
                if self.l2_threshold is not None and self.l2_threshold > 0:
                    l2_line = self.canvas.axs[0].axhline(y=self.l2_threshold, color='orange',
                                                       linestyle='--', alpha=0.8, linewidth=2,
                                                       label=f'L2: {self.l2_threshold} ADC')
                    self.threshold_lines.append(l2_line)
                
                # Update legend
                self.canvas.axs[0].legend()
                print(f" Threshold display: {self.threshold_message}")
            else:
                print(f" {self.threshold_message}")
                # Add text annotation showing no thresholds available
                text_annotation = self.canvas.axs[0].text(0.02, 0.98, self.threshold_message,
                                                        transform=self.canvas.axs[0].transAxes,
                                                        verticalalignment='top', fontsize=10,
                                                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
                self.threshold_lines.append(text_annotation)
            
            # Force canvas update
            self.canvas.fig.canvas.draw()
            print(f"Plot setup complete - ADC range: [-50, 600], Baseline range: [{bl-20}, {bl+20}]")
            
            # Start timer
            self.timer.start(self.update_interval)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText(" Acquiring data...")
            
        except Exception as e:
            print(f" Start error: {e}")
            self.status_label.setText(f" Start error: {e}")

    def stop_data_acquisition(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(" Stopped")

    def clear_data(self):
        # Clear all three subplots (ADC, Baseline, Preload)
        for i in range(len(self.canvas.axs)):
            self.canvas.x_data_arr[i].clear()
            self.canvas.y_data_arr[i].clear()
            self.canvas.lines[i].set_data([], [])
        self.counter = 0
        
        # Clear and re-add threshold lines
        for line in self.threshold_lines:
            line.remove()
        self.threshold_lines.clear()
        
        # Re-add thresholds if available
        if self.l1_threshold is not None:
            l1_line = self.canvas.axs[0].axhline(y=self.l1_threshold, color='red',
                                               linestyle='--', alpha=0.8, linewidth=2,
                                               label=f'L1: {self.l1_threshold} ADC')
            self.threshold_lines.append(l1_line)
            
            if self.l2_threshold is not None and self.l2_threshold > 0:
                l2_line = self.canvas.axs[0].axhline(y=self.l2_threshold, color='orange',
                                                   linestyle='--', alpha=0.8, linewidth=2,
                                                   label=f'L2: {self.l2_threshold} ADC')
                self.threshold_lines.append(l2_line)
            
            self.canvas.axs[0].legend()
        elif hasattr(self, 'threshold_message'):
            # Add "No thresholds available" message if no thresholds
            text_annotation = self.canvas.axs[0].text(0.02, 0.98, self.threshold_message,
                                                    transform=self.canvas.axs[0].transAxes,
                                                    verticalalignment='top', fontsize=10,
                                                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
            self.threshold_lines.append(text_annotation)
        
        # Reset plot titles to show feature information
        self.canvas.axs[0].set_title('HID++ Feature 0x9402: Touch ADC Values', fontsize=10, pad=15)
        self.canvas.axs[1].set_title('HID++ Feature 0x9402: Baseline Variations', fontsize=10, pad=15)
        self.canvas.axs[2].set_title('HID++ Feature 0x9402: Preload Values', fontsize=10, pad=15)
        self.canvas.fig.canvas.draw()

    def update_plot(self):
        if not self.sensor_available or not self.sensing_feature:
            return
            
        try:
            self.counter += 1
            measurement_result = self.sensing_feature.read_measurement(0)
            
            # Add detailed logging every 10th reading to avoid spam
            if self.counter % 10 == 0:
                print(f"Reading #{self.counter}: {measurement_result}")
            
            if measurement_result is None:
                print("Sensor communication lost")
                self.stop_data_acquisition()
                self.status_label.setText(" Sensor communication lost")
                return
            
            # Handle different result formats
            try:
                if isinstance(measurement_result, (list, tuple)) and len(measurement_result) >= 3:
                    new_measurement, bl, pl = measurement_result
                else:
                    # Handle single value or unexpected format
                    new_measurement = measurement_result if isinstance(measurement_result, (int, float)) else 0
                    bl = 0
                    pl = 0
                    if self.counter % 10 == 0:  # Log format issue occasionally
                        print(f"Note: Using single value {new_measurement} from {measurement_result}")
            except Exception as e:
                print(f"Error unpacking measurement: {e}")
                new_measurement, bl, pl = 0, 0, 0
            
            # Add data to all three plot arrays (ADC, Baseline, Preload)
            self.canvas.x_data_arr[0].append(self.counter)
            self.canvas.y_data_arr[0].append(new_measurement)
            self.canvas.x_data_arr[1].append(self.counter)
            self.canvas.y_data_arr[1].append(bl)
            self.canvas.x_data_arr[2].append(self.counter)
            self.canvas.y_data_arr[2].append(pl)
            
            # Debug: Print data being added every 10th reading
            if self.counter % 10 == 0:
                print(f"Plot Update #{self.counter}: ADC={new_measurement}, BL={bl}")
                print(f"  Array lengths: ADC={len(self.canvas.x_data_arr[0])}, BL={len(self.canvas.x_data_arr[1])}")
                print(f"  X data range: {min(self.canvas.x_data_arr[0]) if self.canvas.x_data_arr[0] else 'empty'} to {max(self.canvas.x_data_arr[0]) if self.canvas.x_data_arr[0] else 'empty'}")
                print(f"  ADC range: {min(self.canvas.y_data_arr[0]) if self.canvas.y_data_arr[0] else 'empty'} to {max(self.canvas.y_data_arr[0]) if self.canvas.y_data_arr[0] else 'empty'}")
            
            # Update status with sensitivity info if available
            status_text = f" #{self.counter} ADC: {new_measurement}, BL: {bl}, PL: {pl}"
            if self.sensitivity_adc_per_n is not None:
                # Convert current ADC to force in Newtons
                force_n = new_measurement / self.sensitivity_adc_per_n
                force_g = force_n * 1000 / 9.81  # Convert back to grams equivalent
                status_text += f" | Force: {force_n:.2f}N ({force_g:.0f}g)"
            self.status_label.setText(status_text)
            
            # Update plot lines with current data for all three subplots
            x_data_adc = list(self.canvas.x_data_arr[0])
            y_data_adc = list(self.canvas.y_data_arr[0])
            x_data_bl = list(self.canvas.x_data_arr[1])
            y_data_bl = list(self.canvas.y_data_arr[1])
            x_data_pl = list(self.canvas.x_data_arr[2])
            y_data_pl = list(self.canvas.y_data_arr[2])
            
            self.canvas.lines[0].set_data(x_data_adc, y_data_adc)
            self.canvas.lines[1].set_data(x_data_bl, y_data_bl)
            self.canvas.lines[2].set_data(x_data_pl, y_data_pl)
            
            # Adjust x limits for scrolling effect
            if self.counter >= self.canvas.max_points:
                x_min = self.counter - self.canvas.max_points + 1
                x_max = self.counter
            else:
                x_min = 0
                x_max = self.canvas.max_points
            
            # Set x limits for both plots
            for ax in self.canvas.axs:
                ax.set_xlim(x_min, x_max)
            
            # Auto-scale Y axis occasionally to handle dynamic range, including thresholds
            if self.counter % 20 == 0 and len(y_data_adc) > 10:
                # Auto-scale ADC plot based on recent data (last 20 points)
                recent_adc = y_data_adc[-20:]
                adc_min = min(recent_adc)
                adc_max = max(recent_adc)
                
                # Include threshold values in range calculation to ensure they're always visible
                values_to_include = [adc_min, adc_max]
                if self.l1_threshold is not None:
                    values_to_include.append(self.l1_threshold)
                if self.l2_threshold is not None and self.l2_threshold > 0:
                    values_to_include.append(self.l2_threshold)
                
                # Calculate range including thresholds
                final_min = min(values_to_include)
                final_max = max(values_to_include)
                total_range = final_max - final_min
                margin = max(50, total_range * 0.1)  # At least 50 units margin
                
                self.canvas.axs[0].set_ylim(final_min - margin, final_max + margin)
                
                # Auto-scale Baseline plot based on recent data (last 20 points)
                if len(y_data_bl) > 10:
                    recent_bl = y_data_bl[-20:]
                    bl_min = min(recent_bl)
                    bl_max = max(recent_bl)
                    bl_range = bl_max - bl_min
                    bl_margin = max(10, bl_range * 0.2)  # At least 10 units margin, 20% of range
                    
                    self.canvas.axs[1].set_ylim(bl_min - bl_margin, bl_max + bl_margin)
                
                if self.counter % 40 == 0:  # Less frequent debug
                    threshold_info = ""
                    if self.l1_threshold is not None:
                        threshold_info = f" (includes L1:{self.l1_threshold}"
                        if self.l2_threshold is not None and self.l2_threshold > 0:
                            threshold_info += f", L2:{self.l2_threshold}"
                        threshold_info += ")"
                    print(f"  Auto-scaled ADC: [{final_min - margin:.0f}, {final_max + margin:.0f}]{threshold_info}")
                    
                    # Debug info for baseline auto-scaling
                    if len(y_data_bl) > 10:
                        recent_bl = y_data_bl[-20:]
                        bl_min = min(recent_bl)
                        bl_max = max(recent_bl)
                        bl_range = bl_max - bl_min
                        bl_margin = max(10, bl_range * 0.2)
                        print(f"  Auto-scaled Baseline: [{bl_min - bl_margin:.1f}, {bl_max + bl_margin:.1f}]")

            # Force canvas redraw
            self.canvas.fig.canvas.draw_idle()  # Use draw_idle for better performance
            
        except Exception as e:
            print(f"Update error: {e}")
            self.stop_data_acquisition()
            self.status_label.setText(f" Update error: {e}")

    def closeEvent(self, event):
        """Handle window close event with cleanup"""
        print("Window closing, performing cleanup...")
        self.timer.stop()
        if self.mouse:
            self.mouse.disconnect()

if __name__ == "__main__":
    print(f"Starting Bravo Sensor Viewer v{__version__} ({__build_date__})...")
    
    app = QApplication(sys.argv)
    window = BravoSensorWindow()
    
    # Auto-connect on startup
    window.connect_device()
    
    window.show()
    sys.exit(app.exec_())