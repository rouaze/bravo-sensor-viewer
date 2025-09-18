import logging
from pyhidpp import DevicesManager
from pyhidpp.security import SecurityManager

devManager = DevicesManager(log_to_console=True, log_level=logging.DEBUG)
dev = devManager.connect_with_name("PRO X 2")
dev.enumerate_all()
securityManager = SecurityManager(dev)
try:
  securityManager.unlock_device()
except KeyError:
  print("Password not present in the password file")
dev.disconnect()
