from .feature import Feature
from ..core.utils import DEVICE_TYPE, list_to_u32_le


class X0005(Feature):
    feature_id = 0x0005

    def get_device_type(self):
        res = self.construct_and_process_request(function_nb=2, params=[])

        if res is None:
            self.logger.warning("x0005_getDeviceType response none")
            return None
        return DEVICE_TYPE[list_to_u32_le(res.params[:4])]

    def get_device_name_count(self):
        res = self.construct_and_process_request(function_nb=0, params=[])

        if res is None:
            self.logger.warning("x0005_getDeviceNameCount response none")
            return None
        nameCount = res.params[0]
        return nameCount

    def get_device_name(self, nameCount):
        callNumber = nameCount // 16
        name = []
        for c in range(callNumber + 1):
            params = [0x00] * 3
            params[0] = 16 * (c)
            res = self.construct_and_process_request(function_nb=1, params=params)

            if res is None:
                self.logger.warning("x0005_getDeviceName response none")
                return None

            name += [chr(i) for i in res.params]
        name = "".join(name).rstrip("\x00")
        return name
