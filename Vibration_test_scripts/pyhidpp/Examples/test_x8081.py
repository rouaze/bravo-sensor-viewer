import logging
from pyhidpp.core.devices_manager import DevicesManager
import time

dev_man = DevicesManager(log_to_console=True, log_level=logging.DEBUG)

kbd = dev_man.connect_with_name("PRO X TKL")


if kbd:
    kbd.enumerate_all()

    zones = [1, 3, 6]
    RGBs = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]
    kbd.features.x8081.setIndividualRgbZones(zones, RGBs)

    
    kbd.features.x8081.setRangeRgbZones([10], [56], [[255, 255, 0]])

    kbd.features.x8081.frameEnd() # apply

    time.sleep(3)
    

    kbd.disconnect()