from .feature import Feature
from ..core.utils import (
    list_to_u16_be,
    list_to_u32_be,
    u16_to_list_be,
)


class X9201(Feature):
    feature_id = 0x9201

    # [0] getCapabilities() -> capabilities
    def getCapabilities(self):
        res = self.construct_and_process_request(function_nb=0, params=[0] * 16)
        product_number = list_to_u16_be(res.params[:2])
        major_version = list_to_u16_be(res.params[2:4])
        minor_version = list_to_u16_be(res.params[4:6])
        return product_number, major_version, minor_version

    # [1] readSensorRegister(sensorIdx, regAddr) → RegAddr, regVal
    def read_sensor_register(self, reg_addr, length):
        data = [0] * 16
        data[0:1] = u16_to_list_be(reg_addr)
        data[2] = length
        res = self.construct_and_process_request(function_nb=1, params=data)
        reg_val = res.params[0]
        if length == 2:
            reg_val = list_to_u16_be(res.params[0:2])
        if length == 4:
            reg_val = list_to_u32_be(res.params[0:4])
        return reg_val

    # [2] writeSensorRegister(sensorIdx, regAddr, regVal)
    def write_sensor_register(self, reg_addr, length, reg_val):
        data = [0] * 16
        data[0:2] = u16_to_list_be(reg_addr)
        data[2] = length
        data[3:7] = u16_to_list_be(reg_val)
        res = self.construct_and_process_request(function_nb=2, params=data)
        return res

    # [3] shutdownSensor()
    def shutdown_sensor(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=3, params=data)
        return res

    # [4] resetSensor()
    def reset_sensor(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=4, params=data)
        return res

    # [5] setMonitorMode(count, mode)
    def setMonitoringMode(self, count, mode):
        data = [0] * 16
        data[0:2] = u16_to_list_be(count)
        data[2] = mode
        res = self.construct_and_process_request(function_nb=5, params=data)
        return res

    # [6] startCalibration()
    def start_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=6, params=data)
        return res

    # [7] stopCalibration() → calibrationData
    def stop_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=7, params=data)
        nb_turns = res.params[0]
        min_a = list_to_u16_be(res.params[1:3])
        min_b = list_to_u16_be(res.params[3:5])
        max_a = list_to_u16_be(res.params[5:7])
        max_b = list_to_u16_be(res.params[7:9])
        return nb_turns, min_a, min_b, max_a, max_b

    # [8] readCalibration() → calibrationData
    def read_calibration(self):
        data = [0] * 16
        res = self.construct_and_process_request(function_nb=8, params=data)
        nb_turns = res.params[0]
        min_a = list_to_u16_be(res.params[1:3])
        min_b = list_to_u16_be(res.params[3:5])
        max_a = list_to_u16_be(res.params[5:7])
        max_b = list_to_u16_be(res.params[7:9])
        return nb_turns, min_a, min_b, max_a, max_b

    # [9] writeCalibration(calibrationData)
    def write_calibration(
        self, nb_turns, min_x, max_x, min_y, max_y
    ):
        data = [0] * 16
        data[0] = nb_turns
        data[1, 3] = u16_to_list_be(min_x)
        data[3, 5] = u16_to_list_be(min_y)
        data[5, 7] = u16_to_list_be(max_x)
        data[7, 9] = u16_to_list_be(max_y)
        res = self.construct_and_process_request(function_nb=9, params=data)
        return res

    # [event0] monitorReport() → monitorData
    monitor_report_event = 0

    def decode_monitor_data(self, monitor_data):
        angle = list_to_u16_be(monitor_data[0:2])
        internval = list_to_u16_be(monitor_data[2:4])
        rotation = monitor_data[4]
        slot = monitor_data[5]
        ratchet = monitor_data[6]
        proxiTouch = monitor_data[7]
        proxFusion = list_to_u16_be(monitor_data[8:10])
        counter = list_to_u16_be(monitor_data[14:])
        return (
            angle,
            internval,
            rotation,
            slot,
            ratchet,
            proxiTouch,
            proxFusion,
            counter,
        )
