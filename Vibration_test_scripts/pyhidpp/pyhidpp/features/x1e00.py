from .feature import Feature


class X1E00(Feature):
    feature_id = 0x1E00

    def get_enable_hidden_features(self):
        res = self.construct_and_process_request(function_nb=0, params=[])

        if res is None:
            self.logger.warning("get enable hidden features response none")
            return None

        return res.params[0]

    def set_enable_hidden_features(self, enable):
        res = self.construct_and_process_request(function_nb=1, params=[int(enable)])

        if res is None:
            self.logger.warning("set enable hidden features response none")
            return None

        return res
