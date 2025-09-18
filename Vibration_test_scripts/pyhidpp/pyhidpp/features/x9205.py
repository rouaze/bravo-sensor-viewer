from .feature import Feature
from ..core.utils import list_to_i16_be, list_to_u16_be, list_to_i8, list_to_u8, u16_to_list_be

class X9205(Feature):
    feature_id = 0x9205

    # [0] readSensorRegister(sensorIdx, regAddr) → RegAddr, regVal
    def read_sensor_register(self, sensor_idx, reg_addr):
        data = [0] * 16
        data[0] = reg_addr
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=0, params=data)
        reg_addr = res.params[0]
        reg_val = list_to_u16_be(res.params[1:3])
        return reg_addr, reg_val

    # [1] writeSensorRegister(sensorIdx, regAddr, regVal)
    def write_sensor_register(self, sensor_idx, reg_addr, reg_val):
        data = [0] * 16
        data[0] = reg_addr
        data[1:3] = u16_to_list_be(reg_val)
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=1, params=data)
        return res

    # [2] resetSensor(sensorIdx)
    def reset_sensor(self, sensor_idx):
        data = [0] * 16
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=2, params=data)
        return res

    # [3] shutdownSensor(sensorIdx)
    def shutdown_sensor(self, sensor_idx):
        data = [0] * 16
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=3, params=data)
        return res

    # [4] monitorTest(sensorIdx, count, threshold, mode)
    def monitor_test(self, sensor_idx, count, threshold, mode):
        data = [0] * 16
        data[0:2] = u16_to_list_be(count)
        data[2] = threshold
        data[3] = mode
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=4, params=data)
        return res

    # [5] startCalibration(sensorIdx)
    def start_calibration(self, sensor_idx):
        data = [0] * 16
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=5, params=data)
        return res

    # [6] stopCalibration(sensorIdx) → calibrationData
    def stop_calibration(self, sensor_idx):
        data = [0] * 16
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=6, params=data)
        nb_turns = res.params[0]
        min_x = list_to_u16_be(res.params[1:3])
        max_x = list_to_u16_be(res.params[3:5])
        min_y = list_to_u16_be(res.params[5:7])
        max_y = list_to_u16_be(res.params[7:9])
        min_z = list_to_u16_be(res.params[9:11])
        max_z = list_to_u16_be(res.params[11:13])
        return nb_turns, min_x, max_x, min_y, max_y, min_z, max_z

    # [7] readCalibration(sensorIdx) → calibrationData
    def read_calibration(self, sensor_idx):
        data = [0] * 16
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=7, params=data)
        nb_turns = res.params[0]
        min_x = list_to_u16_be(res.params[1:3])
        max_x = list_to_u16_be(res.params[3:5])
        min_y = list_to_u16_be(res.params[5:7])
        max_y = list_to_u16_be(res.params[7:9])
        min_z = list_to_u16_be(res.params[9:11])
        max_z = list_to_u16_be(res.params[11:13])
        return nb_turns, min_x, max_x, min_y, max_y, min_z, max_z

    # [8] writeCalibration(sensorIdx, calibrationData)
    def write_calibration(self, sensor_idx, nb_turns, min_x, max_x, min_y, max_y, min_z, max_z):
        data = [0] * 16
        data[0] = nb_turns
        data[1, 3] = u16_to_list_be(min_x)
        data[3, 5] = u16_to_list_be(max_x)
        data[5, 7] = u16_to_list_be(min_y)
        data[7, 9] = u16_to_list_be(max_y)
        data[9, 11] = u16_to_list_be(min_z)
        data[11, 13] = u16_to_list_be(max_z)
        data[15] = sensor_idx
        res = self.construct_and_process_request(function_nb=8, params=data)
        return res
    
    # [event0] monitorReport() → monitorData
    monitor_report_event = 0

    def decode_monitor_data(self, monitor_data):
        field_x = list_to_i16_be(monitor_data[0:2])   # signed
        field_y = list_to_i16_be(monitor_data[2:4])   # signed
        field_z = list_to_i16_be(monitor_data[4:6])   # signed
        temp = list_to_u16_be(monitor_data[6:8])   # unsigned
        angle = list_to_u16_be(monitor_data[8:10])   # unsigned
        slot = list_to_i8(monitor_data[10:11])   # signed
        ratchet = list_to_i8(monitor_data[11:12])   # signed
        angle_offset = list_to_i8(monitor_data[12:13])   # signed
        angle_ratchet_nbr = list_to_u8(monitor_data[13:14])   # unsigned
        count = list_to_u16_be(monitor_data[14:16])   # unsigned
        return field_x, field_y, field_z, temp, angle, slot, ratchet, angle_offset, angle_ratchet_nbr, count
