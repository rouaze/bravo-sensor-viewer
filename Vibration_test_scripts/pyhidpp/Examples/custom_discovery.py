# %%
from pyhidpp import HIDPPInterface, DeviceInfo, ConnectedDevice
import hid

# %%
all_itf = hid.enumerate(0x046D)
# %%
pro_wheel_itfs = list(
    filter(lambda i: i["product_string"] == "PRO Racing Wheel for Xbox/PC", all_itf)
)
pro_wheel_itf = HIDPPInterface(
    pro_wheel_itfs[0], pro_wheel_itfs[1], pro_wheel_itfs[2], False
)
pro_wheel_device = DeviceInfo(
    pro_wheel_itf.long["vendor_id"],
    pro_wheel_itf.long["product_id"],
    pro_wheel_itf,
    pro_wheel_itf.long["product_string"],
    0xFF,
    False,
    False,
)
prowheel = ConnectedDevice(pro_wheel_device)
# %%
prowheel.enumerate_all()
