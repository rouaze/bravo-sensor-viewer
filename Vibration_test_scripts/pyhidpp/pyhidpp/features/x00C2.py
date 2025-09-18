from .feature import Feature
import time


class X00C2(Feature):
    feature_id = 0x00C2

    def start_dfu(self):
        """
        this feature will likely restart the device, thus no response is expected.
        For proper use, after this function, we need to reset the module.
        """
        params = [0x00] * 7
        params[0] = 1  # enterDFU
        params[1] = 0  # dfuControlParam, unused
        params[4] = ord("D")
        params[5] = ord("F")
        params[6] = ord("U")

        # stop listener, otherwise it will throw an error when the device is restarting,
        # not present (OS error read)
        self.hidpp.stop_listener_thread()

        # send request
        self.construct_and_process_request(function_nb=1, params=params)

        time.sleep(1.5)

        self.hidpp.reconnect_with_name()
