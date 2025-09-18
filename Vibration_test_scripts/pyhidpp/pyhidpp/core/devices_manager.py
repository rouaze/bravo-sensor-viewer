from .logger import get_pyhidpp_logger
from .discovery import get_interfaces_list, list_devices
from .device_info import DeviceInfo
from .connected_device import ConnectedDevice

import platform
import logging


class DevicesManager:
    devices: list[DeviceInfo]

    def __init__(
        self,
        vid=0x046D,
        dev_type=None,
        log_level=logging.INFO,
        log_to_file=True,
        log_to_console=False,
        display_devices=False,
    ):
        self.system = platform.platform().split("-")[0]

        self.logger = get_pyhidpp_logger(log_level, log_to_file, log_to_console)
        # build endpoints and devices
        self.interfaces_list = get_interfaces_list(vid)
        self.devices = list_devices(self.interfaces_list)
        self.print_discovered()
        if dev_type is not None:
            self.devices = self.get_devices_type(dev_type)
        # self.devices = self.__sort_ble_devices(self.devices)

        # print discovered devices
        if display_devices:
            self.print_discovered()

    def print_discovered(self):
        """pretty print the discovered device"""
        for dev in self.devices:
            self.logger.info(dev)

    def connect_with_name(self, dev_name: str):
        for dev in self.devices:
            if dev_name == dev.name:
                return ConnectedDevice(dev)
        self.logger.info("Device not found")
        return None

    def connect_with_pid(self, pid):
        for dev in self.devices:
            if dev.pid == pid:
                return ConnectedDevice(dev)
        self.logger.info("Device not found")
        return False

    def connect_with_pid_tid(self, pid, tid):
        for dev in self.devices:
            if dev.pid == pid:
                connected_dev = ConnectedDevice(dev)
                if connected_dev.device_info.tid == tid:
                    return connected_dev
                connected_dev.disconnect()
        self.logger.info("Device not found")
        return None

    def get_devices_list(self):
        return self.devices

    def get_devices_type(self, type):
        devices = []
        for devInfo in self.devices:
            if devInfo.dev_type is not None:
                if devInfo.dev_type == type:
                    devices.append(devInfo)
            else:
                dev = ConnectedDevice(devInfo)
                dev_type = dev.features.x0005.get_device_type()
                if dev_type == type:
                    devices.append(devInfo)
                dev.disconnect()
        return devices

    def get_devices_list_str(self):
        devices_list = []
        i = 0
        for dev in self.get_devices_list():
            idx = str(dev.sub_idx) if dev.sub_idx != 0xFF else ""
            devices_list.append("[{}] {:04X} {}-{}".format(i, dev.pid, idx, dev.name))
            i += 1

        return devices_list
