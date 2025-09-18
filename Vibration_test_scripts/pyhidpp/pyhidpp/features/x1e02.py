from .feature import Feature


class X1E02(Feature):
    feature_id = 0x1E02

    def get_info(self):
        res = self.construct_and_process_request(0, [])
        if res is not None:
            support_bit_map = res.params[0]
            persist_bit_map = res.params[1]
            state_bit_map = res.params[2]
            return [support_bit_map, persist_bit_map, state_bit_map]

    def get_react_info(self):
        res = self.construct_and_process_request(3, [])
        if res is not None:
            auth_feature = res.params[0] << 8 | res.params[1]
            return auth_feature

    def disable_features(self, disable_bit_map):
        return self.construct_and_process_request(1, [disable_bit_map])

    def enable_features(self, enable_bit_map):
        return self.construct_and_process_request(2, [enable_bit_map])
