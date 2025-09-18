from .feature import Feature
from ..core.utils import (
    list_to_u16_be,
    u16_to_list_be,
)


class X9203(Feature):
    feature_id = 0x9203

    # [0] readSensorRegister(regAddr) → regVal
    def read_sensor_register(self, reg_addr):
        data = [0] * 16
        data[0] = reg_addr
        res = self.construct_and_process_request(function_nb=0, params=data)
        reg_val = res.params[0]
        return reg_val

    # [1] writeSensorRegister(regAddr, regVal)
    def write_sensor_register(self, reg_addr, reg_val):
        data = [0] * 16
        data[0] = reg_addr
        data[1] = reg_val
        res = self.construct_and_process_request(function_nb=1, params=data)
        return res

    # [2] shutdownSensor()
    def shutdown_sensor(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=2, params=data)
        return res

    # [3] resetSensor()
    def reset_sensor(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=3, params=data)
        return res

    # [4] setMonitorMode(count, mode)
    def setMonitoringMode(self, count, mode):
        data = [0] * 16
        data[0:2] = u16_to_list_be(count)
        data[2] = mode
        res = self.construct_and_process_request(function_nb=4, params=data)
        return res

    # [5] startCalibration()
    def start_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=5, params=data)
        return res

    # [6] stopCalibration() → calibrationData
    def stop_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=6, params=data)
        nb_turns = res.params[0]
        min_a = list_to_u16_be(res.params[1:3])
        max_a = list_to_u16_be(res.params[3:5])
        min_b = list_to_u16_be(res.params[5:7])
        max_b = list_to_u16_be(res.params[7:9])
        return nb_turns, min_a, min_b, max_a, max_b

    # [7] readCalibration() → calibrationData
    def read_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=7, params=data)
        nb_turns = res.params[0]
        min_a = list_to_u16_be(res.params[1:3])
        max_a = list_to_u16_be(res.params[3:5])
        min_b = list_to_u16_be(res.params[5:7])
        max_b = list_to_u16_be(res.params[7:9])
        return nb_turns, min_a, min_b, max_a, max_b

    # [8] writeCalibration(calibrationData)
    def write_calibration(self, nb_turns, min_x, max_x, min_y, max_y):
        data = [0] * 16
        data[0] = nb_turns
        data[1, 3] = u16_to_list_be(min_x)
        data[3, 5] = u16_to_list_be(max_x)
        data[5, 7] = u16_to_list_be(min_y)
        data[7, 9] = u16_to_list_be(max_y)
        res = self.construct_and_process_request(function_nb=8, params=data)
        return res

    # [event0] monitorReport() → monitorData
    monitor_report_event = 0

    def decode_monitor_data(self, monitor_data):
        angle = list_to_u16_be(monitor_data[0:2])
        rotation = monitor_data[2]
        slot = monitor_data[3]
        ratchet = monitor_data[4]
        proxi_touch = monitor_data[5]
        rotation_speed = list_to_u16_be(monitor_data[6:8])
        counter = list_to_u16_be(monitor_data[12:14])
        return (
            angle,
            rotation,
            slot,
            ratchet,
            proxi_touch,
            rotation_speed,
            counter,
        )
