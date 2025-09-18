from .feature import Feature
from ..core.utils import list_to_u16_be

class X1876(Feature):
    feature_id = 0x1876

    def get_hw_info(self):
        """
        Returns:
            nbColumns [8-bit]
            The number of columns in DUT key matrix

            nbRows [8-bit]
            The number of rows in DUT key matrix

            timeoutUs [8-bit]
            The timeout of IR LED emitting time and it’s configurable via function [5]. Unit: micro second
        """
        res = self.construct_and_process_request(function_nb=0, params=[])

        if res is None:
            self.logger.warning("X1876 get_hw_info response none")
            return 0, 0, 0

        nbCols = res.params[0]
        nbRows = res.params[1]
        irTimeUs = res.params[2]

        return nbCols, nbRows, irTimeUs

    def init_test(self):
        """ Test framework, especially stop the switch scanning """
        return self.construct_and_process_request(function_nb=3, params=[])

    def get_key_release_timings(self, columnIdx):
        """ retunr the min and max fall time duration of the specified column idx """
        res = self.construct_and_process_request(function_nb=4, params=[columnIdx])
        if res is None:
            self.logger.warning("X1876 get_key_release_timings response none")
            return 0.0, 0.0

        resolution_us = 1/16

        minDuration_us = list_to_u16_be(res.params[0:2]) * resolution_us
        maxDuration_us = list_to_u16_be(res.params[2:4]) * resolution_us

        return minDuration_us, maxDuration_us

    def config_emit_time(self, emitTimeUs):
        """ change the IR led pulse duration (default is 25 us) """
        return self.construct_and_process_request(function_nb=5, params=[emitTimeUs])

    def end_test(self):
        """ resumne normal operation - switch scanning """
        return self.construct_and_process_request(function_nb=6, params=[])