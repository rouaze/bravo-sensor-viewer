from .feature import Feature


class X2111(Feature):
    feature_id = 0x2111

    def get_capabilities(self):
        res = self.construct_and_process_request(function_nb=0, params=[])

        if res is None:
            self.logger.warning("x2111_getCapabilities response none")
            return None

        tunableTorque = res.params[0]
        autoDisangage = res.params[1] / 4  # in tr/s
        defaultTorque = res.params[2]  # Given in %
        maxForce = res.params[3]  # Given in gF

        return tunableTorque, autoDisangage, defaultTorque, maxForce

    def get_ratchet_control_mode(self):
        res = self.construct_and_process_request(function_nb=1, params=[])

        if res is None:
            self.logger.warning("x2111_getRatchetControlMode response none")
            return None

        wheelMode = res.params[0]
        autoDisangage = res.params[1]  # in tr/s
        defaultTorque = res.params[2]  # Given in %

        return wheelMode, autoDisangage, defaultTorque

    def set_ratchet_control_mode(self, wheelMode, autoDisangage, tunableTorque):
        params = [0 for i in range(3)]

        params[0] = wheelMode
        params[1] = autoDisangage
        params[2] = tunableTorque

        res = self.construct_and_process_request(function_nb=2, params=params)

        if res is None:
            self.logger.warning("x2111_setRatchetControlMode response none")
            return None

        return None
