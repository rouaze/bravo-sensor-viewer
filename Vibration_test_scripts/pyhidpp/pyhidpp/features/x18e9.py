from .feature import Feature
import struct


class X18E9(Feature):
    feature_id = 0x18e9

    def get_state(self):
        res = self.construct_and_process_request(function_nb=0, params=[])
        if res is None:
            self.logger.warning("get_state response none")
            return None
        return res.params[0]

    def set_state(self, active):
        res = self.construct_and_process_request(function_nb=1, params=[int(active)])
        if res is None:
            self.logger.warning("set_state response none")
            return None
        return res

    def read_currents(self):
        res = self.construct_and_process_request(function_nb=2, params=[])
        if res is None:
            self.logger.warning("read_currents response none")
            return None
        phase1 = struct.unpack('>h', bytes(res.params[0:2]))[0]   # int16
        phase2 = struct.unpack('>h', bytes(res.params[2:4]))[0]   # int16
        phase3 = struct.unpack('>h', bytes(res.params[4:6]))[0]   # int16
        return phase1, phase2, phase3

    def get_calibration_value(self, index):
        res = self.construct_and_process_request(function_nb=3, params=[index])
        if res is None:
            self.logger.warning("get_calibration_value response none")
            return None
        return struct.unpack('>h', bytes(res.params[0:2]))[0]   # int16

    def set_calibration_value(self, index, value):
        value_lst = list(struct.pack('>h', value))   # int16
        res = self.construct_and_process_request(function_nb=4, params=[index] + value_lst)
        if res is None:
            self.logger.warning("set_calibration_value response none")
            return None
        return res