import logging
import time
from pyhidpp import DevicesManager
from pyhidpp.security import SecurityManager

channel = 2
power = 0x06
timeout = 1000
condition = 0
radiomode = 0

# Connect to device
devManager = DevicesManager(log_to_console=True, log_level=logging.INFO)
dev = devManager.connect_with_name("Slim Solar+")
dev.enumerate_all()

# Enable 'Compliance Mode'
securityManager = SecurityManager(dev)
try:
  securityManager.unlock_device('COMPL')
except KeyError:
  print("Password not present in the password file")

# Start continuous carrier wave mode: the device will disconnect, the script waits until the 
# rf test is finished and the device reconnects to terminate
try:
  dev.features.x1891.RFTxCW(channel, power, timeout, condition, radiomode)
  time.sleep(1)
  while True:
    if dev.connected:
      break
except KeyboardInterrupt:
  print("Operation interrupted by user.")
finally:
  dev.disconnect()
