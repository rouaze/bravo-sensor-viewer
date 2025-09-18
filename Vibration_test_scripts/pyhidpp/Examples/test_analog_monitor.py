import logging
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.core.utils import list_to_u16_be, list_to_u16_le
import time
import numpy as np
import statistics

monitor_buffer_len = 1000 
monitor_data_buffer = np.zeros(monitor_buffer_len)
monitor_data_ptr = 0

timeout_out_s = 3

## select monitor mode
# monitor_mode = 0x80 # Get Hall sensor raw data (2-byte)
# monitor_mode = 0x81 # Get Hall sensor calibrated segment (1-byte).
monitor_mode = 0x83 # Get Hall sensor Analog values (1-byte)

# NOT WORKING TODAY
# monitor_mode = 0x86 # Get Average calibrated data and noise (3-byte)
# monitor_mode = 0x87 # Get Average calibrated bottom data and noise (3-byte)
# monitor_mode = 0x89 # Get Average calibrated top data and noise (3-byte)
# monitor_mode = 0x8D # 0x8D: Get Hall sensor top baseline (2-byte).



def keyMonitorNotif(req, ts):
    global monitor_mode, monitor_data_buffer, monitor_data_ptr
    # print(req.params)
    if(monitor_mode == 0x81 or monitor_mode == 0x83):
        # value is 1 byte wide
        value = req.params[0]
        print(value, '-'*value)

    elif(monitor_mode == 0x80):
        # value is 2 byte wide
        value = list_to_u16_le(req.params[0:2])
        print(value, '-'*int(value/30))

    elif(monitor_mode == 0x86  or monitor_mode == 0x87):
        # first 2 bytes are average value, 3rd is noise
        value_avg = list_to_u16_le(req.params[0:2])
        value_noise = req.params[2]
        print("0x86 - avg: {}, noise: {}\n".format(value_avg, value_noise))
        return # do not do further processing (like append buffer and stuff)

    # append data into buffer until it is full
    if monitor_data_ptr<monitor_buffer_len:
        monitor_data_buffer[monitor_data_ptr] = value
        monitor_data_ptr += 1

    # if array is full, compute average, std and print
    if(monitor_data_ptr == monitor_buffer_len):
        #print(monitor_data_buffer)
        avg = statistics.mean(monitor_data_buffer)
        std = statistics.stdev(monitor_data_buffer)

        print("avg: {} \tmin: {} \tmax: {} \tstd: {}".format(avg, np.min(monitor_data_buffer), np.max(monitor_data_buffer), std))
        
        # reset
        monitor_data_ptr = 0



dev_man = DevicesManager(log_to_console=True, log_level=logging.DEBUG)

kbd = dev_man.connect_with_name("PRO X TKL")

if kbd:
    kbd.enumerate_all()

    kbd.features.x1E00.set_enable_hidden_features(True)

    kbd.register_notif(0x3615, 0, keyMonitorNotif)

    kbd.features.x3615.startMonitorKey(key='A', mode=monitor_mode, count=10)

    # infinite loop until Ctr-C KeyboardInterrupt
    t_stop = time.time() + timeout_out_s
    try:
        while(time.time() < t_stop):
             time.sleep(0.1)
             
    except KeyboardInterrupt:
        print('exit')

    kbd.features.x3615.stopMonitorKey(mode=monitor_mode)
    kbd.disconnect()