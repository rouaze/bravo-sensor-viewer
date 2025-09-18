from .feature import Feature


class X1E22(Feature):
    feature_id = 0x1E22

    def get_nb_devices(self):
        res = self.construct_and_process_request(0, [])
        if res is not None:
            return res.params[0]

    def get_selected_device(self):
        res = self.construct_and_process_request(1, [])
        if res is not None:
            return [res.params[0], res.params[1] & 0b1, res.params[1] >> 1 & 0b1]

    def select_device(self, device_id, access_config):
        return self.construct_and_process_request(2, [device_id, access_config])

    def spi_direct_access(self, n_bytes: int, data_in: list[int]):
        return self.construct_and_process_request(3, [n_bytes] + data_in)
