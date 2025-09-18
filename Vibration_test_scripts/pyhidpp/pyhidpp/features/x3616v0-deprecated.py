from .feature import Feature
from ..core.utils import u16_to_list_be
import time

GALVATRON_KEY_ID_US = ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', ' =', 'US Backspace', 'Tab', 'Q', 'W', 'E', 'R', 'F', 'D', 'S', 'A', 'Capslock', 'US Shift_L', 'Z', 'X', 'C', 'T', 'Y', 'U', 'I', 'O', 'L', 'K', 'J', 'H', 'G', 'V', 'B', 'N', 'M', ',', 'P', '[', ']', '\\' , 'US Enter', "'", ';', '.', '/', 'US Shift_R', 'Ctrl_L', 'Win', 'Alt_L', 'Space', 'Alt_R', 'FN', 'APP', 'Ctrl_R', 'Print', 'Scroll Lock', 'Pause', 'Page-Up', 'Home', 'Ins', 'Del', 'End', 'Page-Down', 'Up', 'Right', 'Down', 'Left']
GALVATRON_MONITOR_MODE_CALIB_SEGMENT = 0x81
GALVATRON_MONITOR_SETUP_TIME = 2.5

# DEVLOPMENT FEATURE ONLY - FOR ENG PURPOSE
# https://docs.google.com/document/d/1TpgoVm9LVIEHbRPYDTLPEr2JEgN3CqptURTrvhfMD4I/edit#heading=h.mn4ob8ygrtd3 
# 

class X3616V0(Feature):
    feature_id = 0x3616

    def setModeNormal(self):
        self.setAnalogKeyMode(0xFF, 0x00, [0x00])

    def setModeRapidTrigger(self):
        self.setAnalogKeyMode(0xFF, 0x00, [0x01])

    def setNormalModeParams(self, make_level, break_delta):
        self.setNormalTrigger(0xFF, 0x00, data=[make_level, break_delta])

    def setRTParams(self, make_delta, break_delta, threshold, threshold_enable):
        self.setRapidTrigger(0xFF, 0x00, data=[make_delta, break_delta, threshold, threshold_enable])


    # [1] setAnalogKeyMode(infoNbr, offset, data)
    def setAnalogKeyMode(self, infoNbr, offset, data):
        """
            WIP.
            Parameters
            infoNbr
            Number of data info (payload) sent. Limited by the HIDPP payload size.
            HIDPP long: 		max. 14-byte.
            HIDPP extra long:	max. 58-byte.


            If infoNbr = 0xFF all keys are written with data[0] values.
            offset
            Index of the first info data. The full data Info is equal to the Gtech GTY51 sensor number.
            Offset < GtechSensor number - infoNbr 
            data[infoNbr]
            Analog key mode:
            0x00: Normal Trigger
            0x01: Rapid Trigger
            0x02: Rapid Trigger with threshold
            0x03: Multi-points Trigger
            Size needs to be equal to the infoNbr parameter.

        """
        payload = [infoNbr, offset]
        payload.extend(data)
        res = self.construct_and_process_request(function_nb=1, params=payload)
        return None

    # [2]  getAnalogKeyMode( infoNbr, offset) → infoNbr, offset, data
    def getAnalogKeyMode(self, infoNbr, offset):
        """
            Get the analog mode for all keys or individual keys.
            for return format check --> https://docs.google.com/document/d/1TpgoVm9LVIEHbRPYDTLPEr2JEgN3CqptURTrvhfMD4I/edit
        """
        payload = [infoNbr, offset]
        res = self.construct_and_process_request(function_nb=2, params=payload)
        return res

    # [3] setNormalTrigger(infoNbr, offset, data)
    def setNormalTrigger(self, infoNbr, offset, data):
        """
            WIP.
        Parameters
        infoNbr
        Number of data info (payload) sent. Limited by the HIDPP payload size.
        HIDPP long: 		max. 14-byte.
        HIDPP extra long:	max. 58-byte.


        If infoNbr = 0xFF all keys are written with normalTriggerData[0] values.
        offset
        Index of the first info data. The full data Info is equal to the Gtech GTY51 sensor number.
        Offset < GtechSensor number - infoNbr 
        normalTriggerData[infoNbr]
        rapidTriggerData has 2-byte size:
        DeltaLo: 	Press level to generate a Make		(8-bit)
        DeltaHi: 	Release delta  to generate a Break		(8-bit)

        """
        
        payload = [infoNbr, offset]
        payload.extend(data)
        res = self.construct_and_process_request(function_nb=3, params=payload)
        return None

    # [4]  getNormalTrigger( infoNbr, offset) → infoNbr, offset, data
    def getNormalTrigger(self, infoNbr, offset):
        """
            Get the both analog thresholds to detect Make and Break action.
            For all keys or individual keys.
            for return format check --> https://docs.google.com/document/d/1TpgoVm9LVIEHbRPYDTLPEr2JEgN3CqptURTrvhfMD4I/edit
        """
        payload = [infoNbr, offset]
        res = self.construct_and_process_request(function_nb=4, params=payload)
        return res



    # [5] setRapidTrigger(infoNbr, offset, data)
    def setRapidTrigger(self, infoNbr, offset, data):
        """
            WIP.
            Parameters
            infoNbr
            Number of data info (payload) sent. Limited by the HIDPP payload size.
            HIDPP long: 		max. 14-byte.
            HIDPP extra long:	max. 58-byte.


            If infoNbr = 0xFF all keys are written with rapidTriggerData[0] values.
            offset
            Index of the first info data. The full data Info is equal to the Gtech GTY51 sensor number.
            Offset < GtechSensor number - infoNbr 
            rapidTriggerData[infoNbr]
            rapidTriggerData has 4-byte size:
            DeltaLo: 	Press delta to generate a Make		(8-bit)
            DeltaHi: 	Release delta  to generate a Break		(8-bit)
            Threshold: 	Minimum press value to start rapid trigger 	(8-bit)
            ThresholdEnabled: Active Threshold feature is 1
    
        """
        payload = [infoNbr, offset]
        payload.extend(data)
        res = self.construct_and_process_request(function_nb=5, params=payload)
        return None

    # [6]  getRapidTrigger( infoNbr, offset) → infoNbr, offset, data
    def getRapidTrigger(self, infoNbr, offset):
        """
            Get the different threshold values and delta motions to detect Make and Break action.
            For all keys or individual keys.
            for return format check --> https://docs.google.com/document/d/1TpgoVm9LVIEHbRPYDTLPEr2JEgN3CqptURTrvhfMD4I/edit
        """
        payload = [infoNbr, offset]
        res = self.construct_and_process_request(function_nb=6, params=payload)
        return res

    # [9] setAnalogInfo(status, reportRate)
    def setAnalogInfo(self, status, reportRate):
        """
            Start analog info notification. Returns analog key value in HIDPP (see notif description).
        """
        payload = [status, reportRate]
        res = self.construct_and_process_request(function_nb=9, params=payload)
        return res



    


    