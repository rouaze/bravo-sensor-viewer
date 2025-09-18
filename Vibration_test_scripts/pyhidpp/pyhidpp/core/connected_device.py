"""
Simple HIDPP implementation based on Jerome Amiguet's tiresias software
"""

import sys
from typing import Callable
import hid
import time
import logging

from threading import Thread, Event
import queue

import platform

from .request import HIDPPRequest
from ..features.features import Features
from .device_info import DeviceInfo
from datetime import datetime

HIDPP_RESPONSE_LENGTH = 20
SUPPORTED_OS = ["macOS", "Windows"]


class ConnectedDevice:
    """
    HIDPP module implementation
    """

    device_info: DeviceInfo

    def __init__(
        self,
        device_info: DeviceInfo,
        buffer_in_queue=None,
        buffer_out_queue=None,
        software_id=0x0F,
    ):
        if buffer_in_queue is None or buffer_out_queue is None:
            self.buffer_in = queue.Queue()
            self.buffer_out = queue.Queue()
        else:
            self.buffer_in = buffer_in_queue
            self.buffer_out = buffer_out_queue

        self.connected = True
        self.device_info = device_info

        self.sw_id = software_id
        self.features = Features(self)
        self.system = platform.platform().split("-")[0]
        self.dev = not (getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))

        self.logger = logging.getLogger("hidpp")

        self.hidpp_response_length = HIDPP_RESPONSE_LENGTH
        self.is_using_very_long = False

        self.listener_stop_signal = Event()
        self.commander_stop_signal = Event()
        self.registered_notif = {}
        self.deconnection_callback: Callable | None = None
        self.reconnection_callback: Callable | None = None

        if self.system == "macOS":
            self.__start_communication_thread(device_info)
        else:
            self.__start_listener_thread(device_info)
            self.__start_commander_thread(device_info)

    def disconnect(self):
        self.stop_listener_thread()
        self.stop_commander_thread()
        if self.connected:
            self.logger.info(
                "Disconnected from device: {}".format(self.device_info.name)
            )
            self.hidpp_response_length = 20
            self.registered_notif = {}

    def set_custom(self, custom):
        self.custom = custom(self)

    def register_notif(self, feature_id, notif_id, callback):
        if not self.device_info.is_enumerated(feature_id):
            self.logger.warning("Could not register notif. Feature is not enumerated")
            return
        f_idx = self.device_info.features[feature_id].idx

        self.unregister_notif(feature_id, notif_id)

        key = str(f_idx) + ":" + str(notif_id)
        self.registered_notif.update({key: callback})

    def unregister_notif(self, feature_id, notif_id):
        if not self.device_info.is_enumerated(feature_id):
            self.logger.warning("Could not unregister notif. Feature is not enumerated")
            return
        f_idx = self.device_info.features[feature_id].idx
        key = str(f_idx) + ":" + str(notif_id)
        self.registered_notif.pop(key, None)

    def get_buffer_in_req(self):
        """
        get request from input queue
        """
        if not self.buffer_in.empty():
            res = self.buffer_in.get_nowait()
            return res
        else:
            return None

    def wait_notif(self, timeout_s=2):
        """
        wait for an incoming notification
        """
        delay = 0.001
        max_attempt = int(timeout_s / delay)

        res = self.get_buffer_in_req()
        attempt = 1
        while res is None and attempt < max_attempt:
            res = self.get_buffer_in_req()
            attempt += 1
            time.sleep(delay)
        self.clear_input_queue()
        return res

    def clear_input_queue(self):
        with self.buffer_in.mutex:
            self.buffer_in.queue.clear()

    def clear_output_queue(self):
        with self.buffer_out.mutex:
            self.buffer_out.queue.clear()

    def send_req_and_wait_response(self, req, timeout=0.2) -> HIDPPRequest | None:
        """
        send a HIDpp request and wait for the response
        """
        # before sending anything, best to see if there is anything in the input queue
        # already
        res = self.get_buffer_in_req()
        while res is not None:
            self.logger.warning(
                "unprocessed IN req: idx:{}, feature:{}, fct: {}, params:{}".format(
                    res.dev_idx, res.feature, res.function, res.params
                )
            )
            res = self.get_buffer_in_req()

        self.buffer_out.put_nowait(req)

        try:
            res = self.buffer_in.get(timeout=timeout)
        except queue.Empty:
            # still empty after timeout
            return None

        # workaround when notif are sended between request and response
        # (ie the response we get is a notification, that was sent inbetween,
        # and not the response of the request)
        if self.__isTheResponse(req, res):
            return res
        else:
            max_attempt = 10
            attempt = 0
            while attempt < max_attempt:
                attempt += 1
                # the response we get is not the answer. A notification was received
                # just before. Thus we swap the 2 last request
                self.logger.warning(
                    "a notif was received before the request's response"
                )
                if res is not None:
                    self.logger.warning(
                        f"unprocessed IN req: idx:{res.dev_idx}, feature:{res.feature},"
                        f" fct: {res.function}, params:{res.params}"
                    )

                # temp = res

                try:
                    res = self.buffer_in.get(timeout=timeout)
                except queue.Empty:
                    res = None

                if self.__isTheResponse(req, res):
                    # discard the unwanted notif, don't put back in buffer
                    """# put back the notif in the buffer for further process
                    self.buffer_in.put_nowait(temp)"""
                    self.clear_input_queue()
                    return res
        return res

    def send_raw(self, req_list):
        req = HIDPPRequest(from_list=req_list)
        res = self.send_req_and_wait_response(req)
        return res

    def send_raw_no_rep(self, req_list):
        req = HIDPPRequest(from_list=req_list)
        self.buffer_out.put_nowait(req)
        return None

    def send_custom_request(self, feature_id, function_nb, params):
        if not self.connected:
            self.logger.warning("ERROR: device is not connected")
            return None

        dev_idx = self.device_info.sub_idx

        if self.device_info.is_enumerated(feature_id):
            feature_idx = self.device_info.features[feature_id].idx
        else:
            self.logger.warning("Feature id:{} is not enumerated".format(feature_id))
            return None

        if len(params) > 20:
            req_type = "VERY LONG"
        elif len(params) > 3:
            req_type = "LONG"
        else:
            req_type = "SHORT"

        req = HIDPPRequest(
            dev_idx=dev_idx,
            feature=feature_idx,
            function=function_nb,
            req_type=req_type,
            params=params,
        )
        res = self.send_req_and_wait_response(req, timeout=1)
        return res

    def send_custom_request_no_rep(self, feature_id, function_nb, params):
        if not self.connected:
            self.logger.warning("ERROR: device is not connected")
            return None

        dev_idx = self.device_info.sub_idx

        if self.device_info.is_enumerated(feature_id):
            feature_idx = self.device_info.features[feature_id].idx
        else:
            self.logger.warning("Feature id:{} is not enumerated".format(feature_id))
            return None

        if len(params) > 20:
            req_type = "VERY LONG"
        elif len(params) > 3:
            req_type = "LONG"
        else:
            req_type = "SHORT"

        req = HIDPPRequest(
            dev_idx=dev_idx,
            feature=feature_idx,
            function=function_nb,
            req_type=req_type,
            params=params,
        )
        #res = self.send_req_and_wait_response(req, timeout=1)
        self.buffer_out.put_nowait(req)
        return None

    def enumerate_feature(self, f_id):
        if not self.connected:
            return False

        if self.device_info.is_enumerated(f_id):
            return True

        f = self.features.x0000.get_feature(f_id)
        if f.idx == 0:  # idx 0 means not found
            return False

        self.device_info.add_feature(f)
        return True

    def enumerate_all(self):
        if not self.connected:
            return False

        if not self.device_info.is_enumerated(0x0001):
            if not self.enumerate_feature(0x0001):
                return False

        cnt = self.features.x0001.get_count()

        for idx in range(2, cnt + 1):
            f_info = self.features.x0001.get_feature_id(idx)
            self.device_info.add_feature(f_info)

        self.device_info.print_features_set()
        return True

    def stop_listener_thread(self):
        self.listener_stop_signal.set()
        try:
            self.thread_in.join()
        except AttributeError:
            # thread_in not instanciated
            pass

    def stop_commander_thread(self):
        self.commander_stop_signal.set()
        try:
            self.thread_out.join()
        except AttributeError:
            # thread_out not instanciated
            pass

    """ PRIVATE METHODS
        not to be used outside this class
    """

    def __listener(
        self,
        dev,
        stop_event,
        h_in_long,
        h_in_short=None,
        h_in_extra_long=None,
        sleep=0.0002,
    ):
        """
        listen to HIDpp request from the connected device

        to run in dedicated thread (see connect call)
        when a IN hid request is received, it is put in the input queue
        """

        while not stop_event.is_set():
            if h_in_short is not None:  # no short endpoint for ble
                ret = h_in_short.read(10)
                if len(ret) > 0:
                    self.logger.debug(
                        "SHORT R: [{}]".format(", ".join(hex(x) for x in ret))
                    )
                    req = HIDPPRequest(from_list=ret)
                    # req.print_request_props()
                    # connection notif: link unestablished
                    if (
                        req.feature == 0x41
                        and req.dev_idx == dev.sub_idx
                        and (req.params[0] >> 6) & 0x01 == 1
                    ):
                        self.logger.info("Device link lost")
                        self.connected = False
                        if self.deconnection_callback is not None:
                            self.deconnection_callback()
                    elif (
                        req.feature == 0x41
                        and req.dev_idx == dev.sub_idx
                        and (req.params[0] >> 6) & 0x01 == 0
                    ):
                        # connection notif: link established
                        self.logger.info("Device link established")
                        self.connected = True
                        if self.reconnection_callback is not None:
                            self.reconnection_callback()

            ret = h_in_long.read(self.hidpp_response_length)
            if len(ret) > 0:
                self.logger.debug("LONG R: [{}]".format(", ".join(hex(x) for x in ret)))
                req = HIDPPRequest(from_list=ret)

                if not self.__processNotif(req):
                    self.buffer_in.put_nowait(req)

            if h_in_extra_long is not None:
                ret = h_in_extra_long.read(self.hidpp_response_length)
                if len(ret) > 0:
                    self.logger.debug(
                        "EXTRA LONG R: [{}]".format(", ".join(hex(x) for x in ret))
                    )
                    req = HIDPPRequest(from_list=ret)

                    if not self.__processNotif(req):
                        self.buffer_in.put_nowait(req)

            time.sleep(sleep)

        if h_in_short is not None:  # no short endpoint for ble
            h_in_short.close()
        h_in_long.close()
        if h_in_extra_long is not None:
            h_in_extra_long.close()

    def __commander(self, dev, stop_event, h_out_long, sleep=0.0002):
        """
        send HIDpp request to the connected device

        to run in dedicated thread (see connect call)
        when a OUT hid request/command is in the output queue, it is sent to the device
        important: all command are send to the long endpoint (short are converted)
        """

        # h_out_short = hid.device()
        # h_out_short.open_path(dev.interface.endpoint_short['path'])
        # h_out_short.set_nonblocking(1)

        while not stop_event.is_set():
            if not self.buffer_out.empty():
                req = self.buffer_out.get_nowait()
                req_list = req.build_request()  # build_request

                # short are sent on the long endpoint (need convertion)
                if req.req_type == "SHORT":
                    req.req_type = "LONG"
                    req_list[0] = 0x11
                    req_list.extend([0] * (20 - len(req_list)))
                    req.length = 20

                # both long and very long are sent on the same endpoint
                # but we need to transform long request into very long ones
                if req.req_type == "LONG" and self.is_using_very_long:
                    req.req_type = "VERY LONG"
                    req_list[0] = 0x12
                    req_list.extend([0] * (64 - len(req_list)))
                    req.length = 64

                self.logger.debug(
                    "LONG W: [{}]".format(", ".join(hex(x) for x in req_list))
                )
                if req.req_type == "LONG" or req.req_type == "VERY LONG":
                    h_out_long.write(req_list)
                else:
                    # h_out_short.write(req_list)
                    pass
            time.sleep(sleep)

        # h_out_short.close()
        h_out_long.close()

    def __processNotif(self, req):
        ts = datetime.now()
        notif_id = req.function
        f_idx = req.feature
        key = str(f_idx) + ":" + str(notif_id)
        if req.sw_id == 0 and notif_id <= 0x0F:  # is a notif
            if key in self.registered_notif.keys():
                # call the specific registered callback linked to this notif
                self.registered_notif[key](req, ts)
                return True
        return False

    def __start_listener_thread(self, dev: DeviceInfo):
        h_in_short = None
        if dev.interface.has_short():  # no short endpoint for ble
            h_in_short = hid.device()
            h_in_short.open_path(dev.interface.short["path"])
            h_in_short.set_nonblocking(1)

        h_in_long = hid.device()
        h_in_long.open_path(dev.interface.long["path"])
        h_in_long.set_nonblocking(1)

        h_in_extra_long = None
        if dev.interface.has_xl():
            h_in_extra_long = hid.device()
            h_in_extra_long.open_path(dev.interface.extra_long["path"])
            h_in_extra_long.set_nonblocking(1)

        self.clear_input_queue()
        self.thread_in = Thread(
            target=self.__listener,
            args=(
                dev,
                self.listener_stop_signal,
                h_in_long,
                h_in_short,
                h_in_extra_long,
            ),
        )
        self.thread_in.start()

    def __start_commander_thread(self, dev):
        h_out_long = hid.device()
        h_out_long.open_path(dev.interface.long["path"])
        h_out_long.set_nonblocking(1)

        self.clear_output_queue()
        self.thread_out = Thread(
            target=self.__commander, args=(dev, self.commander_stop_signal, h_out_long)
        )
        self.thread_out.start()

    def __start_communication_thread(self, dev):
        h_out_long = hid.device()
        h_out_long.open_path(dev.interface.endpoint_long["path"])
        h_out_long.set_nonblocking(1)

        self.clear_output_queue()
        self.thread_out = Thread(
            target=self.__commander, args=(dev, self.commander_stop_signal, h_out_long)
        )
        self.thread_out.start()
        self.clear_input_queue()
        self.thread_in = Thread(
            target=self.__listener, args=(dev, self.listener_stop_signal, h_out_long)
        )
        self.thread_in.start()

    def __isTheResponse(self, req, res: HIDPPRequest):
        """
        check if res is the response of the request req
        """
        if req is None or res is None:
            return False

        # error handling
        if res.feature == 0xFF:
            rebuilt_feature = res.function << 4 | res.sw_id
            if req.feature == rebuilt_feature:
                return True

        if (
            req.feature == res.feature
            and req.function == res.function
            and req.sw_id == res.sw_id
        ):
            return True
        else:
            return False

    def __get_response_length(self):
        """routine to test with what report length the device is sending back
        default is hidpp long request, but could be hidpp very long as well"""

        # send dummy hidpp feature and look at response to get its type
        res = self.send_custom_request(0x0000, 0, [0, 0, 0])
        if res is not None:
            if res.req_type == "LONG":
                # all ok
                return True
            elif res.req_type == "VERY LONG":
                # then change response length
                self.hidpp_response_length = 64
                # try again and see result
                res = self.send_custom_request(0x0000, 0, [0, 0, 0])
                if res.req_type == "VERY LONG":
                    # all ok
                    self.logger.info(
                        "Changed hidpp response request length to VERY LONG"
                    )
                    self.is_using_very_long = True
            else:
                self.logger.warning("Response request length is not correct")
            return True
        else:
            self.logger.warning("Response for length not received")
            return False

    def get_device_info(self, print_res=True):
        if not self.connected:
            return

        if not self.device_info.is_enumerated(0x0003):
            if not self.enumerate_feature(0x0003):
                self.logger.warning("No feature 3 when getting device info")
                return

        dev_info = self.features.x0003.get_device_info()
        if dev_info:
            self.device_info.set_device_info(dev_info)

            for entity in range(dev_info.entity_count):
                fw_info = self.features.x0003.get_fw_info(entity)
                self.device_info.add_entity_fw_info(fw_info)
                # add TID number for device, corresponding to the app transport id
                if fw_info.dev_type == 0 and fw_info.active:  # main application
                    self.device_info.tid = fw_info.trPid

            if print_res:
                self.device_info.print_device_info()

    def get_battery_state(self):
        res = self.features.x1004.get_status()
        if res:
            return res
        res = self.features.x1001.get_battery_info()
        if res:
            return res
        return self.features.x1000.get_battery_level_status()
