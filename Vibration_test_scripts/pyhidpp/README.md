# pyhidpp

Python module for hidpp communication with Logitech devices.

(Based on Jerome Amiguet's tiresias software and gannetTuner hidpp stack)

## Requirements

- python >= 3.10: the library packs extensive use of type hints for code clarity
- hidapi: should be automatically installed when using global install / pip install hidapi otherwise
- pycryptodome: pip install pycryptodome

## Installation

### Through pip (preferred)
The preferred, fast and easy way to install pyhidpp is through pip, treating pyhidpp as a standard python library.

Prerequisites:
- a ssh key from your local machine linked to your gitlab account
- a virtual environnement with python >= 3.10 activated

Inside the virtual env, run:
```
pip install git+ssh://git@gitlab.logitech.com/mtx/librairies/pyhidpp.git
```

Once the installation is complete, you can import part of the library inside your project or in a REPL using

```
from pyhidpp import DevicesManager
```


### Submodule

In case you would like a physical copy of PyHIDPP inside your project for better control or custom features, clone the library as a git submodule running:

```
git submodule add git@gitlab.logitech.com:mtx/librairies/pyhidpp.git
```

It can then be used within your project using `from pyhidpp.pyhidpp import HIDPP`

If you want to have the latest features, hop on the dev branch by adding the branch field in the `.gitmodules` file:

```
(...)
[submodule "pyhidpp"]
	path = pyhidpp
	url = git@gitlab.logitech.com:mtx/librairies/pyhidpp.git
	branch = dev
(...)

```

Then run

```
git submodule update --remote
```

## Structure

At the time of writing, the package is comprised of the following namespaces:

- `pyhidpp`: Core module.
  - DevicesManager: device manager,mainly for discovery
  - ConnectedDevice: instance connected to the physical device
  - HIDPPRequest: hidpp resquest definition
  - HIDPPInterface: wrapper for short, long, extra long interfaces
  - DeviceInfo: class for all info related to hw, fw, features etc
  - Features: class packing all the currently implemented features
  - list of utility functions
- `pyhidpp.security`:
  - SecurityManager: usefull to unlock devices. Need key file.
- `pyhidpp.sensor`: Module
  - sensor_autodetect: build the correct sensor class based on transmission reports
  - SensorInterface: similar to HIDPP with a few added utilities for sensor communication
  - various sensor implementations: EM7788, EM7790, EM7795.

Example of imports in your project:

```
from pyhidpp import DevicesManager
from pyhidpp.security import SecurityManager
from pyhidpp.sensor import sensor_autodetect
```

## Usage

### Examples

The repo contains an `examples` folder showing some possible implementations of the librarie.

1. basic.py : Basic interaction with a device through HIDPP.
2. list_sort_devices.py : Find available devices, check there types and display it
3. custom_discovery.py: Make use of the low level hid api to create a device from specific interfaces
4. custom_feature.py: Shows how to implement custom features, which are not already in this lib. Once stable, contributions are welcome!

To run the examples, use the `run & debug` section of VSCode, the `launch.json` file in the `.vscode` folder is configured to run the basic example.
Alternatively using a terminal, run the example as a module:

```
python -m examples.basic
```

### Automatic discovery

The discovery module features a set of algorithms to scan and list common mice and keyboards based on the list of low level HID interfaces exposed by hidapi. The functions `get_interfaces_list` creates a list of HIDPPInterfaces, mapping long and short interfaces and distinguish ble.
`list_devices` creates a list of HIDPPDevice and will poll any receiver and append paired devices to the overall list.
The relevant code is the following:

```python
from pyhidpp import get_interface_list, list_devices

itfs = get_interface_list(0x046D)
devices = list_devices(itfs)
```

The DeviceManager will do this automatically and provide functions to create ConnectedDevices to start talking to the devices:

```python
from pyhidpp import DeviceManager

dev_man = DeviceManager()
mouse = dev_man.connect_with_name("My mouse name")
mouse.enumerate_all()
# your hidpp stuff here
mouse.disconnect()
```

### Send request & read response

```python
# send raw data example (no enumeration needed)
res = device.send_raw([0x10, 0xFF, 0x0C, 0x3F, 0x02, 0x00, 0x00]) # example short hidpp
print(res.params)

# enumeration
device.enumerate_all() # perform a full enumeration, or
device.enumerate_feature(0x0003) # enumerate specific feature, if present on the device

# send custom request example (feature enumeration needed)
res = device.send_custom_request(0x0003, 1, [0x01, 0x00, 0x00]) # feature id, function nb, parameters
print(res.params)

# individual implemented features can be sent like this (feature enumeration needed):
res = device.features.x0003_getDeviceInfo()
print(res.params)
```

### DFU, device FW update

#todo update

```python
# perform a DFU (FW update) (0x00D0 feature enumeration needed)
# defice must be in DFU (bootloader) mode. Can be done with x00C2_startDfu
hidpp.enumerate_feature(0x00D0) # if not done yet
hidpp.load_dfu_file("path\\to\\dfu\\file\\new_fw.dfu") # load dfu file. This will print DFU informations
hidpp.perform_dfu(restart=True) # execute DFU, then restart the device
```

### Custom feature

If the HIDPP feature that you wish to use is not yet part of the library, you can create a class extending the Feature class and implement the relevant methods. Find here an example taken from Salvia:

```python
from .feature import Feature

class XF0FE(Feature):
    feature_id = 0xF0FE

    def setHorizontalScroll(enable: bool):
        res = self.construct_and_process_request(function_nb=1, params=[int(enable)])
```

Then instanciate it feeding it your ConnectedDevice and start using the custom device:

```python
dev_man = DeviceManager()
salvia = dev_man.connect_with_name("Salvia")
f0fe = XF0FE(salvia)
f0fe.setHorizontalScroll(True)
```

### Using low level interfaces

If you are trying to connect to a non convensional device and know precisely which HID endpoints you want to use, you can skip the discovery functions and the device manager altogether and create a ConnectedMouse from raw hidapi interfaces.
Here is the sample code for connecting to the PRO Wheel:

```python
import hid
from pyhidpp import (
    HIDPPInterface,
    HIDPPDevice,
    ConnectedDevice
)

all_itf = hid.enumerate(0x046D)

pro_wheel_itfs = list(
    filter(lambda i: i["product_string"] == "PRO Racing Wheel for Xbox/PC", all_itf)
)
# here I know that in the pro_wheel_itfs, the short is index 0, long is 1 and extra_long is 2
# but it can vary from device to device
pro_wheel_itf = HIDPPInterface(pro_wheel_itfs[0], pro_wheel_itfs[1], pro_wheel_itfs[2], False)
pro_wheel_device = HIDPPDevice(
    pro_wheel_itf.long["vendor_id"],
    pro_wheel_itf.long["product_id"],
    pro_wheel_itf,
    pro_wheel_itf.long["product_string"],
    0xFF,
    False,
    False,
)
prowheel = ConnectedDevice(pro_wheel_device)
prowheel.enumerate_all()
# etc...
```

## Security

The security package allows to use feature 1602 to switch a device into manufacturing mode.
A password called `passwords_enc_mecha.ini` is required to do so, ask [Virgile](https://gitlab.logitech.com/vhernicot) in case you want to use this service. Then place the file in your main python file's folder or at your prefered location and optionally set the custom path:
```python
# if case the file is placed in the parent folder
security_manager = SecurityManager(device, tdeOffuscatedFileName=".\\..\\passwords_enc_mecha.ini")
```

## Developement

### Limitation

#### Compatible devices

The library can connect to:

- Wireless devices (receiver, UFY, LS)
- BLEpro receiver
- BLE device

Other devices have not been tested. Minor tweeks can be required to connect to other HID devices.

#### HIDpp

The library works well with devices that communicate on the LONG endpoint (in and out).
All trafic is done on the long endpoint.
**Short request are converted to long and sent on the LONG endpoint**

VERY LONG endpoint not ready yet.

Listener thread opens the IN SHORT endpoint as well to listen to (dis)connect notif from receiver.

#### Dealing with multiple (same) device

When multiple devices with the same name are connected to your PC, the module will connect to the first one that it sees when using the _connect_with_name_, or _connect_with_pid_ method.

A solution is to select a specific device. Example:

```python
dev_man = DeviceManager()
for dev in dev_man.devices:
    print(dev.name)
my_dev = dev_man.devices[3]
device = ConnectedDevice(my_dev)
```

### Currently implemented hidpp features

- X0000
- X0001
- X0003
- X0005
- X00C2
- X00D0
- X1000
- X1001
- X1004
- X1602
- X1876
- X1890
- X1891
- X18E9
- X1B08
- X1E00
- X1E02
- X1E22
- X1E30
- X2111
- X2202
- X3617
- X6100
- X8081
- X8100
- X8128
- X8129
- X9201
- X9203
- X9205
- X9209
- X920B
- X92D1
- XF008

**Note** Feel free to submit new lib version with additional **Generic functions**

### Known issue

## Support

If you use pyhidpp on one of your projects, please list it [here](https://docs.google.com/spreadsheets/d/1TsRqDMiNy5iWR2QuWJL6g2rUs6hHW1fpgSj7FDRacnQ/edit#gid=0) so that we can contact you for updates
