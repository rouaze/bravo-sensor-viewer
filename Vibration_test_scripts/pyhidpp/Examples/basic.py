import logging
from pyhidpp.core.devices_manager import DevicesManager

dev_man = DevicesManager(log_to_console=True, log_level=logging.DEBUG)

pro_x = dev_man.connect_with_name("MX Master 3")

if pro_x:
    pro_x.enumerate_all()

    fancy_name = pro_x.features.x0005.get_device_name(0)

    print(fancy_name)

pro_x.disconnect()