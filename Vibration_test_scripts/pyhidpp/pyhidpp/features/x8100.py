from .feature import Feature


class X8100(Feature):
    feature_id = 0x8100

    def set_onboard_mode(self, mode: int):
        return self.construct_and_process_request(1, [mode])
