from time import sleep
from pyhidpp.core.devices_manager import DevicesManager

def re_callback():
  print("CONNECTION IS BACK!")

def de_callback():
  print("CONNECTION IS LOST!")

dev_man = DevicesManager()

dev = dev_man.connect_with_pid(0xB032)
if dev:
  dev.deconnection_callback = de_callback
  dev.reconnection_callback = re_callback
  sleep(10)
  # try shutting down device and power it back up

  dev.disconnect()