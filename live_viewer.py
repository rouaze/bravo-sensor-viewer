import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from collections import deque
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.security import SecurityManager
from pyhidpp.features.x9402 import X9402
import logging
import time
class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=8, dpi=100):
        # Create figure and axes
        self.fig, self.axs = plt.subplots(2,1,figsize=(width, height), dpi=dpi)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.x_data_arr = []
        self.y_data_arr = []
        self.lines = []
        self.max_points = 200
        self.axs[0].set_title('Real-Time Measurements')
        self.axs[0].set_ylabel('ADC')
        self.axs[1].set_ylabel('Baseline')

        for self.ax in self.axs:
        # Initialize plot settings
            self.ax.set_xlim(0, 100)
            self.ax.set_ylim(-100, 600)
            self.ax.grid(True)
            self.x_data_arr.append(deque(maxlen=self.max_points))
            self.y_data_arr.append(deque(maxlen=self.max_points))
            l, = self.ax.plot([], [], '-')
            self.lines.append( l)


        # Setup figure for better performance
        self.fig.tight_layout()

class LivePlotWindow(QMainWindow):
    def __init__(self):
        super(LivePlotWindow, self).__init__()
        self.setWindowTitle("Live Plotting with PyQt")
        self.resize(800, 600)

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
        
        # Add control buttons
        button_layout = QHBoxLayout()
        self.pltext = QLabel("")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")
        
        self.start_button.clicked.connect(self.start_data_acquisition)
        self.stop_button.clicked.connect(self.stop_data_acquisition)
        self.clear_button.clicked.connect(self.clear_data)
        button_layout.addWidget(self.pltext)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Setup timer for data updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.update_interval = 10  # milliseconds

        self.timerCon = QTimer(self)
        self.timerCon.timeout.connect(self.reconnect)
        self.update_interval = 10  # milliseconds
        
        # Initialize data counter
        self.counter = 0
        
    def start_data_acquisition(self):
        self.timer.start(self.update_interval)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        try:
            measurement_result = self.sensing_feature.read_measurement(0)
            if measurement_result is None:
                print("WARNING: Initial sensor reading failed, using defaults")
                return
            
            new_measurement, bl, pl = measurement_result  # Unpack the tuple
            cal_data = self.sensing_feature.read_cal_data(0)
            
            if cal_data is None:
                print("WARNING: Calibration data not available, using default threshold")
                nom_th = 100
            else:
                # Standalone version returns tuple (nom_th, low_th, high_th)
                try:
                    nom_th, low_th, high_th = cal_data
                    print(f"Calibration data - Nominal: {nom_th}, Low: {low_th}, High: {high_th}")
                except (ValueError, TypeError):
                    print("WARNING: Invalid calibration data format, using default threshold")
                    nom_th = 100

            self.canvas.axs[0].hlines([nom_th,nom_th*2],xmin=0,xmax=100000,color='r',linestyle='--')
            self.canvas.axs[0].set_ylim([-100,nom_th*4])


            self.canvas.axs[1].set_ylim(bl-50,bl+50)
        except Exception as e:
            print(f"At start got {e}")
        
    def stop_data_acquisition(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.mouse.disconnect()
        
    def clear_data(self):
        for i in range(len(self.canvas.axs)):
            self.canvas.x_data_arr[i].clear()
            self.canvas.y_data_arr[i].clear()
            self.canvas.lines[i].set_data([], [])
            self.counter = 0
            self.canvas.fig.canvas.draw()
        
    def update_plot(self):
        # Generate new data point (replace with your actual measurement code)
        self.counter += 1
        try:
            measurement_result = self.sensing_feature.read_measurement(0)
            
            if measurement_result is None:
                raise Exception("Sensor reading failed - device communication error")
                
            new_measurement, bl, pl = measurement_result  # Unpack the tuple
            # Add data
            self.canvas.x_data_arr[0].append(self.counter)
            self.canvas.y_data_arr[0].append(new_measurement)

            self.canvas.x_data_arr[1].append(self.counter)
            self.canvas.y_data_arr[1].append(bl)
            self.pltext.setText(f"Preload:{pl}")
        except Exception as e:
            print(f"Disconnected {e}")
            self.mouse.disconnect()
            self.stop_data_acquisition()
            self.timerCon.start(self.update_interval)
            return
        
        # Update line
        self.canvas.lines[0].set_data(list(self.canvas.x_data_arr[0]), list(self.canvas.y_data_arr[0]))
        self.canvas.lines[1].set_data(list(self.canvas.x_data_arr[1]), list(self.canvas.y_data_arr[1]))
        # Adjust x limits for scrolling effect when enough data is available
        if self.counter >= self.canvas.max_points:
            for ax in self.canvas.axs: 
                ax.set_xlim(self.counter - self.canvas.max_points + 1, self.counter)
        if self.counter <= self.canvas.max_points:
            for ax in self.canvas.axs: 
                ax.set_xlim(0, self.canvas.max_points)

        
        # Redraw canvas
        self.canvas.fig.canvas.draw()

    def closeEvent(self, event):
        """Handle window close event with cleanup"""
        print("Window closing, performing cleanup...")
        self.timer.stop()
        self.timerCon.stop()
        # Clean up resources
        self.mouse.disconnect()

    def reconnect(self):
        for i in range(50):
            time.sleep(0.1)
            dev_manager = DevicesManager(log_to_console=False,log_level=logging.ERROR)
            compatible_mice = ["Malacca", "Bravo"]
            for mouse_name in compatible_mice:
                self.mouse = dev_manager.connect_with_name(mouse_name)
                if self.mouse!=None:
                    # Add device debugging information
                    print(f"Connected to device: {mouse_name}")
                    if hasattr(self.mouse, 'device_info'):
                        info = self.mouse.device_info
                        print(f"Device Info:")
                        print(f"  - Product Name: {getattr(info, 'product_name', 'Unknown')}")
                        print(f"  - Serial: {getattr(info, 'serial', 'Unknown')}")
                        print(f"  - PID: 0x{getattr(info, 'pid', 0):04X}")
                        print(f"  - VID: 0x{getattr(info, 'vid', 0):04X}")
                        print(f"  - Sub Index: {getattr(info, 'sub_idx', 'Unknown')}")
                        print(f"  - Connected: {self.mouse.connected}")
                        if hasattr(info, 'features') and info.features:
                            print(f"  - Available Features: {len(info.features)}")
                            for feat_id, feat_info in info.features.items():
                                print(f"    * 0x{feat_id:04X} at index {feat_info.idx}")
                    break
            if self.mouse == None:
                print("No compatible device found (Malacca/Bravo).")
                continue

            securityManager = SecurityManager(self.mouse,tdeOffuscatedFileName="./passwords_enc_mecha.ini")

            try:
                err = securityManager.unlock_device()
                print(f"Unlock result: {err}")
                print("Malacca unlocked.")
                self.sensing_feature = X9402(self.mouse)
                measurement_result = self.sensing_feature.read_measurement(0)
                
                if measurement_result is None:
                    print("Sensor not responding after unlock, retrying connection...")
                    continue
                
                val, bl_test, pl_test = measurement_result  # Unpack the tuple
                print(f"Sensor reading successful - Val: {val}, Baseline: {bl_test}, Preload: {pl_test}")
                break

            except Exception as e:
                print(f"{e}.")
        self.timerCon.stop()
        self.start_data_acquisition()

if __name__ == "__main__":


    app = QApplication(sys.argv)
    window = LivePlotWindow()
    window.reconnect()
    window.show()
    sys.exit(app.exec_())

