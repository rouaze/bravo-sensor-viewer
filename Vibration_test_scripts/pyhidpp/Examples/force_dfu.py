import hid
from pyhidpp.core.discovery import list_devices, get_interfaces_list

# this script can be used when a device keeps rebooting due to a hardware change 
# to force it to enter DFU mode to update the firmware according to the new hardware

path = None
while path is None:
    itfs = get_interfaces_list(0x46D, 0xf002)
    devs = list_devices(itfs)
    if len(devs) > 0:
        path = devs[0].interface.long["path"]

print(f"found path: {path}")

while True:
    h = hid.device()
    h.open_path(path)
    h.set_nonblocking(1)
    print(h.get_product_string())
    payload = [0x11, 0xFF, 0x0D, 0x1F, 1, 0, 0, 0, 0x44, 0x46, 0x55]
    payload_full = payload + [0] * 7
    print(payload_full)
    h.write(payload_full)
    print("sent")
    p = h.read(20)
    print(p)
