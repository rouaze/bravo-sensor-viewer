from pyhidpp.security import SecurityManager
from pyhidpp.sensor import sensor_autodetect, SensorInterface

devManager = SensorInterface()
devManager.connect_with_name("PRO X 2")
securityManager = SecurityManager(devManager)
securityManager.unlock_device()
sensor = sensor_autodetect(devManager)
devManager.disconnect()
