from .dfu_data import DfuData
from .connected_device import ConnectedDevice
from .utils import printConsoleProgressBar
import logging
from threading import Thread
import time


class DFUController:

    def __init__(self, device: ConnectedDevice):
        self.dfu_data = DfuData()
        self.logger = logging.getLogger("hidpp")
        self.connected_device = device

    def __dfu_send_packet(self, line_nb):
        param_data = self.dfu_data.extract_line(line_nb)
        seqNb = self.dfu_data.get_seqNb()

        # sending packet
        if line_nb == 0:
            # start dfu
            res = self.connected_device.features.x00D0.dfu_start(param_data)
        else:
            res = self.connected_device.features.x00D0.dfu_cmd_data(seqNb, param_data)

        return res

    def __dfu_get_res_status(self, res):
        resp_status = 0
        if res is None:
            # self.logger.info("No response received")
            resp_status = 3  # = fake wait status
        else:
            resp_status = res.params[4]  # response startus
        return resp_status

    def __dfu_default_progress_callback(self, iteration, total):
        printConsoleProgressBar(iteration, total)

    def __dfu_default_error_callback(self, line_nb, params):
        resp_status = params[4]  # response startus

        # not all status code are implemented
        if resp_status == 4:
            self.logger.error("DFU Generic error")
        elif resp_status == 16:
            self.logger.error("DFU Unknown error")
        elif resp_status == 18:
            self.logger.error("DFU Unsupported entity")
        elif resp_status == 20:
            self.logger.error("DFU Bad magic string")
        elif resp_status == 148:
            self.logger.error("DFU Bad magic string")
        else:
            self.logger.error("DFU error {}".format(resp_status))

    def __dfu_error(self, line_nb, res_params, error_callback):
        self.logger.error(
            "\r\nDFU process IN req error. Line nb{}, params:{}".format(
                line_nb, res_params
            )
        )
        if error_callback is not None:
            error_callback(line_nb, res_params)

    def __dfu_process(
            self, timeout_s, progress_callback, error_callback, response_callback, restart
    ):
        self.dfu_data.dfu_ongoing = True
        for line_nb in range(self.dfu_data.tot_line):
            # send data packet
            res = self.__dfu_send_packet(line_nb)

            # evaluate response
            attempt_cnt = 1
            wait_time = 0.001
            resp_ok = False
            while not resp_ok:
                # call response callback (for user specific app)
                if response_callback is not None:
                    response_callback(res)

                # extract response status
                resp_status = self.__dfu_get_res_status(res)

                # act upon response status
                if resp_status == 1:  # success
                    resp_ok = True  # exit loop and continue

                elif resp_status in [2, 5, 6]:  # dfu success status
                    # self.logger.info("Status {}, DFU success".format(resp_status))
                    resp_ok = True  # exit loop

                elif resp_status == 3:  # wait status
                    self.logger.debug("Retry reading response")
                    time.sleep(wait_time)
                    # retry reading IN req (if any, otherwise return None)
                    res = (
                        self.connected_device.get_buffer_in_req()
                    )

                    # manage timeout
                    attempt_cnt += 1  # attempt in reading response
                    if (attempt_cnt * wait_time) > timeout_s:
                        # we need to resend the packet
                        self.logger.warning("Timeout, resend packet")
                        res = self.__dfu_send_packet(line_nb)
                        attempt_cnt = 1  # reset attempt

                else:
                    # most probably an error
                    self.__dfu_error(line_nb, res.params, error_callback)
                    return

            # self.logger.info("DFU Progress: {} %".format(int(100*line_nb/self.dfu_data.tot_line)))
            if progress_callback is not None:
                try:
                    # call progress callback
                    progress_callback(line_nb, self.dfu_data.tot_line)
                except:
                    pass

            self.dfu_data.inc_seqNb()

        # restart ?
        if restart:
            self.connected_device.features.x00D0.restart(self.dfu_data.entityIdx)

        self.dfu_data.dfu_ongoing = False

    def load_dfu_file(self, dfu_filename):
        """load a dfu file"""
        if self.dfu_data.set_dfu_file(dfu_filename):
            self.dfu_data.print_dfu_info()

        # return dfu file info
        return self.dfu_data.get_dfu_info_list()

    def perform_dfu(
            self,
            blocking=True,
            timeout_s=5,
            progress_callback="default",
            error_callback="default",
            response_callback=None,
            restart=True,
    ):
        """Perform a FW update.
        Device must be in DFU mode (can be done with x00C2_startDfu)
        DFU file must have been loaded (load_dfu_file)

        blocking: if True, process wait until completion
            otherwise use is_dfu_ongoing() to check if dfu process is finished,
            or use progress_callback to check last iteration

        restart: if True, sends a restart entity request

        progress_notif_callback is a user settable callback (func(iter, tot)) called a
            each iteration to notify about the progress by default uses
            self.__dfu_default_progress_callback which print a progress bar in console.
        error_callback is a user settable callback (func(line_nb, params)) called when
            a dfu error is received
        response_callback is a user settable callback (func(res)) called for each
            response (for user app scpecific interaction)
        """

        if not self.dfu_data.ready_for_update:
            return

        if not self.connected_device.device.is_enumerated(0x00D0):
            if not self.connected_device.enumerate_feature(0x00D0):
                return

        if progress_callback == "default":
            progress_callback = self.__dfu_default_progress_callback

        if error_callback == "default":
            error_callback = self.__dfu_default_error_callback

        # todo check if device is in DFU (bootloader mode), don't know if possible.
        # perform dfu process
        self.dfu_thread = Thread(
            target=self.__dfu_process,
            args=(
                timeout_s,
                progress_callback,
                error_callback,
                response_callback,
                restart,
            ),
        )
        self.dfu_data.dfu_ongoing = True
        self.dfu_thread.start()

        if blocking:
            # wait until thread is done
            self.dfu_thread.join()

    def is_dfu_ongoing(self):
        if not self.dfu_data.dfu_ongoing:
            return False

        # check if dfu thread is done
        if self.dfu_thread.is_alive():
            return True

        return False
