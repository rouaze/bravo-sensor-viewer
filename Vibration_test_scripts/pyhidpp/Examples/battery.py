import logging
from pyhidpp.core.devices_manager import DevicesManager

devManager = DevicesManager(log_to_console=True)
devManager.get_devices_list()
dev = devManager.connect_with_name("PRO X 2")
if dev:
    print("Requesting state of battery...")
    state = dev.get_battery_state()
    print(state)
    dev.disconnect()