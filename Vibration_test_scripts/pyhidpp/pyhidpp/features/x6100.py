from .feature import Feature


class X6100(Feature):
    feature_id = 0x6100

    def set_raw_report_state(self, rawMode):
        params = [0 for i in range(3)]

        params[0] = rawMode

        res = self.construct_and_process_request(function_nb=2, params=params)

        if res is None:
            self.logger.warning("x6100 set raw report state response none")
            return None

        return None
