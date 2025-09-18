import logging
from pyhidpp import DevicesManager


def list_and_sort(hid: DevicesManager):
    hid_devices = hid.get_devices_list()
    hidppActiveDevices = []
    for idx, device in enumerate((hid_devices)):
        dev_controller = hid.connect_with_name(device.name)
        if dev_controller is not None:
            deviceType = dev_controller.features.x0005.get_device_type()
            tempDict = {"Name": device.name, "Type": deviceType}
            hidppActiveDevices.append(tempDict)
        dev_controller.disconnect()
    return hidppActiveDevices


if __name__ == "__main__":
    hid = DevicesManager(log_level=logging.DEBUG, log_to_console=True, dev_type="Mouse")
    output = list_and_sort(hid)
    print("There is {} active HIDPP devices:".format(len(output)))
    for device in output:
        print("    {} {}".format(device["Name"], device["Type"]))
