from .feature import Feature
import time


class X00D0(Feature):
    feature_id = 0x00D0

    def dfu_cmd_data(self, seqNb, data):
        return self.construct_and_process_request(function_nb=seqNb, params=data)

    def dfu_cmd_data0(self, data):
        return self.dfu_cmd_data(0, data)

    def dfu_cmd_data1(self, data):
        return self.dfu_cmd_data(1, data)

    def dfu_cmd_data2(self, data):
        return self.dfu_cmd_data(2, data)

    def dfu_cmd_data3(self, data):
        return self.dfu_cmd_data(3, data)

    # def x00D0_dfuStart(self, entityIdx, encrypt, magicStrg, flag, securLvl):
    def dfu_start(self, data):
        # params = [0x00]*16

        # params[0] = entityIdx
        # params[1] = encrypt

        # if( len(magicStrg) > 10 ):
        #     self.logger.error("Wrong magicStrg parameter")
        #     return None

        # i = 0
        # for c in magicStrg:
        #     params[2+i] = ord(c)
        #     i += 1

        # params[12] = flag
        # params[13] = securLvl

        return self.construct_and_process_request(function_nb=4, params=data)

    def restart(self, entityIdx=255):
        """
        this feature is supposed to restart the device, thus no response is expected.
        For proper use, after this function, we need to reset the module.
        """
        params = [0x00] * 16
        params[0] = entityIdx

        # stop listener, otherwise it will throw an error when the device is restarting,
        # not present (OS error read)
        self.hidpp.stop_listener_thread()

        # send request
        self.construct_and_process_request(function_nb=5, params=params)

        time.sleep(1.5)

        self.hidpp.reconnect_with_name()
