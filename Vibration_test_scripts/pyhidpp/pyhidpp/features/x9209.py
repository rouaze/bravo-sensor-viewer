from .feature import Feature
from ..core.utils import list_to_i16_be, list_to_u16_be, u16_to_list_be

class X9209(Feature):
    feature_id = 0x9209

    # [0] readSensorRegister(sensorIdx, regAddr) → sensorIdx, RegAddr, regVal
    def read_sensor_register(self, sensor_idx, reg_addr):
        data = [0] * 16
        data[0] = sensor_idx
        data[1] = reg_addr
        res = self.construct_and_process_request(function_nb=0, params=data)
        sensor_idx = res.params[0]
        reg_addr = res.params[1]
        reg_val = list_to_u16_be(res.params[2:4])
        return sensor_idx, reg_addr, reg_val

    # [1] writeSensorRegister(sensorIdx, regAddr, regVal) → sensorIdx, RegAddr, regVal
    def write_sensor_register(self, sensor_idx, reg_addr, reg_val):
        data = [0] * 16
        data[0] = sensor_idx
        data[1] = reg_addr
        data[2:4] = u16_to_list_be(reg_val)
        res = self.construct_and_process_request(function_nb=1, params=data)
        sensor_idx = res.params[0]
        reg_addr = res.params[1]
        reg_val = list_to_u16_be(res.params[2:4])
        return sensor_idx, reg_addr, reg_val

    # [2] resetSensor(sensorIdx) → sensorIdx
    def reset_sensor(self, sensor_idx):
        data = [0] * 16
        data[0] = sensor_idx
        res = self.construct_and_process_request(function_nb=2, params=data)
        sensor_idx = res.params[0]
        return sensor_idx

    # [3] shutdownSensor(sensorIdx) → sensorIdx
    def shutdown_sensor(self, sensor_idx):
        data = [0] * 16
        data[0] = sensor_idx
        res = self.construct_and_process_request(function_nb=3, params=data)
        sensor_idx = res.params[0]
        return sensor_idx

    # [4] monitorTest(sensorIdx, count, threshold) → sensorIdx, count, threshold
    def monitor_test(self, sensor_idx, count, threshold):
        data = [0] * 16
        data[0] = sensor_idx
        data[1:3] = u16_to_list_be(count)
        data[4] = threshold
        res = self.construct_and_process_request(function_nb=4, params=data)
        sensor_idx = res.params[0]
        count = list_to_u16_be(res.params[1:3])
        threshold = res.params[3]
        return sensor_idx, count, threshold

    # [5] startCalibration(sensorIdx) → sensorIdx, minAtan, maxAtan
    def start_calibration(self, sensor_idx):
        data = [0] * 16
        data[0] = sensor_idx
        res = self.construct_and_process_request(function_nb=5, params=data)
        sensor_idx = res.params[0]
        min_atan = list_to_u16_be(res.params[1:3])
        max_atan = list_to_u16_be(res.params[3:5])
        return sensor_idx, min_atan, max_atan

    # [6] stopCalibration(sensorIdx) → sensorIdx, minAtan, maxAtan
    def stop_calibration(self, sensor_idx):
        data = [0] * 16
        data[0] = sensor_idx
        res = self.construct_and_process_request(function_nb=6, params=data)
        sensor_idx = res.params[0]
        min_atan = list_to_u16_be(res.params[1:3])
        max_atan = list_to_u16_be(res.params[3:5])
        return sensor_idx, min_atan, max_atan

    # [7] readCalibration(sensorIdx) → sensorIdx, minAtan, maxAtan
    def read_calibration(self, sensor_idx):
        data = [0] * 16
        data[0] = sensor_idx
        res = self.construct_and_process_request(function_nb=7, params=data)
        sensor_idx = res.params[0]
        min_atan = list_to_u16_be(res.params[1:3])
        max_atan = list_to_u16_be(res.params[3:5])
        return sensor_idx, min_atan, max_atan

    # [8] writeCalibration(sensorIdx, minAtan, maxAtan) → sensorIdx, minAtan, maxAtan
    def write_calibration(self, sensor_idx, min_atan, max_atan):
        data = [0] * 16
        data[0] = sensor_idx
        data[1, 3] = u16_to_list_be(min_atan)
        data[3, 5] = u16_to_list_be(max_atan)
        res = self.construct_and_process_request(function_nb=8, params=data)
        sensor_idx = res.params[0]
        min_atan = list_to_u16_be(res.params[1:3])
        max_atan = list_to_u16_be(res.params[3:5])
        return sensor_idx, min_atan, max_atan
    
    # [9] calibrate(sensorId, refPointIdx, refPointVal) → sensorId, refPointIdx, refPointVal, atan
    def calibrate(self, sensor_idx, ref_point_idx, ref_point_val):
        data = [0] * 16
        data[0] = sensor_idx
        data[1] = ref_point_idx
        data[2] = ref_point_val
        res = self.construct_and_process_request(function_nb=9, params=data)
        sensor_idx = res.params[0]
        ref_point_idx = res.params[1]
        ref_point_val = res.params[2]
        atan = list_to_u16_be(res.params[3:5])
        return sensor_idx, ref_point_idx, ref_point_val, atan

    # [event0] monitorReport() → monitorData
    monitor_report_event = 0

    def decode_monitor_data(self, monitor_data):
        sensor_idx = monitor_data[0]
        field_x = list_to_i16_be(monitor_data[1:3])   # signed
        field_y = list_to_i16_be(monitor_data[3:5])   # signed
        field_z = list_to_i16_be(monitor_data[5:7])   # signed
        temp = list_to_u16_be(monitor_data[7:9])   # unsigned
        atan = list_to_u16_be(monitor_data[9:11])   # unsigned
        count = list_to_u16_be(monitor_data[14:16])   # unsigned
        return sensor_idx, field_x, field_y, field_z, temp, atan, count
