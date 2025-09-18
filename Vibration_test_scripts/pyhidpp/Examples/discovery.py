from pyhidpp import get_interfaces_list, list_devices

interfaces_list = get_interfaces_list(0x046D)
for itf in interfaces_list:
    print(itf)

devices = list_devices(interfaces_list)
for dev in devices:
    print(dev)
