import logging
from pyhidpp.core.connected_device import ConnectedDevice
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.core.request import HIDPPRequest
from pyhidpp.security.security_manager import SecurityManager
import time
import numpy as np

dev_man = DevicesManager(log_to_console=True, log_level=logging.INFO)
device = dev_man.connect_with_name("MX Master 4")
if not device:
    raise Exception("Device not found")
device.enumerate_all()  # perform a full enumeration
securityManager = SecurityManager(device)
securityManager.unlock_device()
device.features.x1E00.set_enable_hidden_features(True)
current_feature = device.features.x9201.feature_id
global_data = []

def my_callback(req: HIDPPRequest, timestamp: int):
    global global_data
    global_data.append(req.params[0:])
    

def start_monitoring(device: ConnectedDevice, num_measurements=0, sensor_index=0x00):
    device.register_notif(
        current_feature, device.features.x9201.monitor_report_event, my_callback
    )
    device.features.x9201.setMonitoringMode(num_measurements, 0b10)

def decode_data(device: ConnectedDevice):
    proc_data = []
    for data in global_data:
        proc_data.append(device.features.x9201.decode_monitor_data(data))
    return proc_data

def getAngleMeasM(device: ConnectedDevice, nbrData: int):
    
        if nbrData is not None:
            start_monitoring(device, nbrData)
            minSamplingFreq = 125  # Hz, 100Hz for MidRange and 125Hz for HighEnd
            time.sleep(nbrData / minSamplingFreq)

            while len(global_data) < nbrData:
                time.sleep(0.1)

        proc_data = decode_data(device)
        a = np.array([d["angle"] for d in proc_data])
        # print("------angle------",angle)
        jitter = np.max(a) - np.min(a)
        # print("------jitter------",jitter)
        if jitter > 180:
            for j in range(len(a)):
                if a[j] > 180:
                    a[j] = 360 - a[j]
        # print("------a------",a)
        return a

    

for i in range(100):
    data = getAngleMeasM(device, 100)
    print(data)
    time.sleep(5)

device.disconnect()
    