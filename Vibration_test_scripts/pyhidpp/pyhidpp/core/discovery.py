from dataclasses import dataclass
import time
import hid

from .utils import (
    BLE_PRO_RECEIVER_PID,
    BOLT_DEVICE_TYPE,
    UNIFYING_RECEIVER_PID,
    list_to_hex_string,
)
from .device_info import DeviceInfo

from .interface import HIDPPInterface
from .request import HIDPPRequest


legacy = 0xFF00
modern = 0xFF43


@dataclass
class Capabilities:
    nb: int
    has_short: bool
    has_long: bool
    has_xl: bool


def get_common_dev_name(devPath: bytes):
    return devPath.decode().split("#")[2][:-1]


def get_capabilities(ord: int):
    hasShort = (ord & 0b1) == 1
    hasLong = (ord & 0b10) == 0b10
    hasExtraLong = (ord & 0b100) == 0b100
    return Capabilities(
        hasExtraLong + hasLong + hasShort,
        hasExtraLong,
        hasLong,
        hasShort,
    )


def get_interfaces_list(vid=0x46D, pid=0):
    raw_devs = hid.enumerate(vendor_id=vid, product_id=pid)

    vendor_devs = [
        d
        for d in raw_devs
        if d["vendor_id"] == vid and d["usage"] and d["usage_page"] and d["path"]
    ]

    by_pid = {}
    for d in vendor_devs:
        if d["product_id"] not in by_pid:
            by_pid[d["product_id"]] = []
        by_pid[d["product_id"]].append(d)

    interfaces = []

    for pid_devices in by_pid.values():
        by_usage_page = {}
        for d in pid_devices:
            if d["usage_page"] not in by_usage_page:
                by_usage_page[d["usage_page"]] = []
            by_usage_page[d["usage_page"]].append(d)

        modern_collection = by_usage_page.get(modern, [])
        legacy_collection = by_usage_page.get(legacy, [])

        if legacy_collection:
            short = [d for d in legacy_collection if d["usage"] == 1]
            long = [d for d in legacy_collection if d["usage"] == 2]

            if len(short) == 1 and len(long) == 1:
                interfaces.append(HIDPPInterface(short[0], long[0]))
            else:
                for dev in long:
                    matching = next(
                        (
                            d
                            for d in short
                            if get_common_dev_name(d["path"])
                            == get_common_dev_name(dev["path"])
                        ),
                        None,
                    )
                    if matching:
                        interfaces.append(HIDPPInterface(matching, dev))

        if modern_collection:
            short = [d for d in modern_collection if d["usage"] & 0xFF == 1]
            long = [d for d in modern_collection if d["usage"] & 0xFF == 2]
            extra_long = [d for d in modern_collection if d["usage"] & 0xFF == 4]

            capabilities = get_capabilities(modern_collection[0]["usage"] >> 8)

            if capabilities.nb == len(modern_collection):
                interfaces.append(
                    HIDPPInterface(
                        short[0] if capabilities.has_short else None,
                        long[0],
                        extra_long[0] if capabilities.has_xl else None,
                    )
                )
            else:
                for dev in long:
                    matching = next(
                        (
                            d
                            for d in short
                            if get_common_dev_name(d["path"])
                            == get_common_dev_name(dev["path"])
                        ),
                        None,
                    )
                    extr_long_match = next(
                        (
                            d
                            for d in extra_long
                            if get_common_dev_name(d["path"])
                            == get_common_dev_name(dev["path"])
                        ),
                        None,
                    )
                    interfaces.append(HIDPPInterface(matching, dev, extr_long_match))

    return interfaces


def list_devices(interfaces_list: list[HIDPPInterface]) -> list[DeviceInfo]:
    devices = []
    # get names
    for interface in interfaces_list:
        # dealing with BLE interface

        endpoint_short = interface.short
        endpoint_long = interface.long

        product_string = endpoint_long["product_string"].replace("_", " ")
        vid = endpoint_long["vendor_id"]
        pid = endpoint_long["product_id"]

        devices.append(DeviceInfo(vid, pid, interface, product_string, 0xFF))

        if pid in BLE_PRO_RECEIVER_PID:
            h_long = hid.device()
            h_long.open_path(endpoint_long["path"])
            h_long.set_nonblocking(1)

            h_short = hid.device()
            h_short.open_path(endpoint_short["path"])
            h_short.set_nonblocking(1)

            for dev_id in range(1, 7):
                h_short.write([0x10, 0xFF, 0x83, 0xB5, 0x50 + dev_id, 0, 0])
                res = h_long.read(20, 100)
                if len(res) > 0:
                    dev_info = res[5]
                    dev_type = dev_info & 0b1111
                    link = dev_info >> 6 & 0b1
                    ble_pid = res[7] << 8 | res[6]
                    h_short.write([0x10, 0xFF, 0x83, 0xB5, 0x60 + dev_id, 1, 0])
                    ret = h_long.read(20, 100)
                    if len(ret) > 0:
                        req = HIDPPRequest(from_list=ret)
                        # params = ret[4:]
                        name_length = req.params[2]
                        name = "".join(
                            [str(chr(x)) for x in req.params[3 : 3 + name_length]]
                        )
                        devices.append(
                            DeviceInfo(
                                vid,
                                ble_pid,
                                interface,
                                name,
                                dev_id,
                                BOLT_DEVICE_TYPE[dev_type],
                                link,
                            )
                        )
            h_long.close()
            h_short.close()
        elif pid in UNIFYING_RECEIVER_PID:
    
            
            h_short = hid.device()
            h_short.open_path(endpoint_short["path"])
            h_short.set_nonblocking(1)

            h_long = hid.device()
            h_long.open_path(endpoint_long["path"])
            h_long.set_nonblocking(1)
            
            for dev_id in range(0, 6): 
                # get name request / UFY
                h_short.write([0x10, 0xFF, 0x83, 0xB5, 0x40 + dev_id, 0, 0])
                time.sleep(0.002)
                # read hidpp long (expected from unifying)
                ret = h_long.read(20)
                if len(ret) > 0:
                    req = HIDPPRequest(from_list=ret)
                    # params = ret[4:]
                    name_length = req.params[1]
                    name = "".join(
                        [str(chr(x)) for x in req.params[2 : 2 + name_length]]
                    )
                    devices.append(DeviceInfo(vid, pid, interface, name, dev_id+1))
                
            """
            # enable notifications on receiver
            h_short.write([0x10, 0xFF, 0x80, 0x80, 0x00, 0x01, 0x00])
            res = h_short.read(7, 100)
            # read various registers (inspired by bazinga)
            h_short.write([0x10, 0xFF, 0x81, 0x00, 0x00, 0x00, 0x00])
            res = h_short.read(7, 100)
            h_short.write([0x10, 0xFF, 0x80, 0x00, 0x00, 0x01, 0x00])
            res = h_short.read(7, 100)
            # get number of devices
            h_short.write([0x10, 0xFF, 0x81, 0x02, 0x00, 0x00, 0x00])
            res = h_short.read(7, 100)
            n_devices = res[5]
            # simulate sync attempt
            h_short.write([0x10, 0xFF, 0x80, 0x02, 0x02, 0x00, 0x00])
            res_41 = []
            for i in range(n_devices):
                i = 0
                res = h_short.read(7, 100)
                # flush any response present before the notifications
                while i < 3 and res[2] != 0x41:
                    res = h_short.read(7, 100)
                    i += 1
                if res[2] == 0x41:
                    res_41.append(res)
            for i in range(n_devices):
                dev_info = res_41[i]
                dev_id = dev_info[1]
                dev_pid = dev_info[6] << 8 | dev_info[5]
                dev_type = BOLT_DEVICE_TYPE[dev_info[4] & 0b1111]
                link = dev_info[4] >> 6 & 0b1
                h_short.write([0x10, 0xFF, 0x83, 0xB5, 0x40 + dev_id - 1, 0, 0])
                # read hidpp long (expected from unifying)
                ret = h_long.read(20, 100)
                if len(ret) > 0:
                    req = HIDPPRequest(from_list=ret)
                    # params = ret[4:]
                    name_length = req.params[1]
                    name = "".join(
                        [str(chr(x)) for x in req.params[2 : 2 + name_length]]
                    )
                    devices.append(
                        DeviceInfo(
                            vid, dev_pid, interface, name, dev_id, dev_type, link
                        )
                    )
            """

            h_short.close()
            h_long.close()

    return devices
