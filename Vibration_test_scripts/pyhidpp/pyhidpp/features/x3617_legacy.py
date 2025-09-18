from .feature import Feature
from ..core.utils import u16_to_list_be
import time


# DEVLOPMENT FEATURE ONLY - FOR ENG PURPOSE
# https://docs.google.com/document/d/1WytjI9bGC-DurBpMuI3z8pjok6G-pLoxKyHviZkOTP0/edit  
# 

class X3617(Feature):
    feature_id = 0x3617
    #feature_id = 0xf008

    # [0] getCapabilities() → analog_mode, analog_key_nbr, analog_resolution
    def getCapabilities(self):
        res = self.construct_and_process_request(function_nb=0, params=[])
        return res

    # [1] setAnalogKeyMode(trigger_cidx, analog_mode)
    def setAnalogKeyMode(self, trigger_cidx, analog_mode):
        """
            trigger_cidx
                CID index of the key.
                If cidx= 0xFF all keys are written with the same analog_mode values.
                analog_mode
            Analog key mode (1-byte):
                0x00: Key disabled
                0x01: Normal trigger
                0x02: Rapid trigger
                0x03: Continuous rapid trigger
                0x04: Multi action trigger
        """
        res = self.construct_and_process_request(function_nb=1, params=[trigger_cidx, analog_mode, 0])
        return res

    # [2] setNormalTrigger(trigger_cidx, actuation_point, hysteresis)
    def setNormalTrigger(self, trigger_cidx, actuation_point, hysteresis):
        """
            trigger_cidx
                CID index of the key.
                If cidx= 0xFF all keys are written with the same actuation_point and hysteresis values.
            actuation_point
                Analog absolute value to generate a make event.
            hysteresis
                Analog hysteresis value,relative to the actuation_point, to generate a break event.
        """
        res = self.construct_and_process_request(function_nb=2, params=[trigger_cidx, actuation_point, hysteresis])
        return res

    # [3] setRapidTrigger(trigger_cidx, actuation_point, sensitivity, continuous_status)
    def setRapidTrigger(self, trigger_cidx, actuation_point, sensitivity, continuous_status=1):
        """
            trigger_cidx
                CID index of the key.
                If cidx= 0xFF all keys are written with the same actuation_point and hysteresis values.
            Actuation_point
                Minimum press value to start rapid trigger processing (trigger of the first Make).
            sensitivity
                Analogue delta trigger value to generate a make or break action.
                The delta starts at the first change in direction of the key movement.
                Any other direction change after the first one is ignored.
            continuous_status
                1: Continuous rapid trigger is enabled
                0: Rapid trigger is disabled above this threshold value.

        """
        res = self.construct_and_process_request(function_nb=3, params=[trigger_cidx, actuation_point, sensitivity, continuous_status])
        return res

    # [4] setMultiAction(trigger_cidx, actuation_point, assignment, actuation_event)
    def setMultiAction(self, trigger_cidx, actuation_point_hi, actuation_point_lo, assignments, actuation_events, mode, hysteresis):
        """
            trigger_cidx
                CID index of the key trigger.
            actuation_point_hi
                1st actuation point level for the multi action triggers.
            actuation_point_lo
                2nd actuation point level for the multi action triggers.
                Actuation_point_lo > Actuation_point_hi
            assignments (array of length 4)
                2 x HID modifier keycode.
                2 x HID normal key keycode.
            actuation_event[assignment][event]
                Actuation event vs. actuationPoints and assignments.
                0 = Released
                1 = Make
                2 = Break
                3 = Pressed
                4 = Make/Break
            Mode
                0 = Full customizable  mode. In this mode the actuation_event parameters need to be set.
                1 = Combine mode. The actuation_event parameters are not used.
                2 = Alternate mode. The actuation_event parameters are not used.

        """

        if(actuation_point_lo <= actuation_point_hi):
            print("x3617 multi actions actuation point parameters error")
            return None

        if(len(assignments) != 4):
            print("x3617 multi actions assignments parameters error")
            return None

        if(len(actuation_events) > 4):
            print("x3617 multi actions actuation_events parameters error")
            return None

        payload = [0]*16
        payload[0] = trigger_cidx
        payload[1] = actuation_point_hi
        payload[2] = actuation_point_lo
        for i in range(4):
            payload[3+i] = assignments[i]

        #TODO: full customizable mode not implemented yet, only ncombine and alternate mode as of now
        i=7
        for act_event in actuation_events:
            if(len(act_event) != 4):
                print("x3617 multi actions events parameters error")
                return None
            payload[i] = (act_event[1]<<4) | act_event[0]
            payload[i+1] = (act_event[3]<<4) | act_event[2]
            i = i+2


        payload[15] = mode<<4 | hysteresis
        print(payload)
        res = self.construct_and_process_request(function_nb=4, params=payload)
        return res

    # [5] setCombineThresholdTrigger(trigger_cidx, combine_cidx, actuation_point)

    # [6] getAnalogKeyMode(trigger_cidx) → trigger_cidx, analog_mode
    def getAnalogKeyMode(self, trigger_cidx):
        res = self.construct_and_process_request(function_nb=6, params=[trigger_cidx, 0, 0])
        return res

    # [7] getNormalTrigger(trigger_cidx) → (trigger_cidx, actuation_point, hysteresis
    def getNormalTrigger(self, trigger_cidx):
        res = self.construct_and_process_request(function_nb=7, params=[trigger_cidx, 0, 0])
        return res

    # [8] getRapidTrigger(trigger_cidx) → (trigger_cidx, actuation_point, sensitivity, continuous_status
    def getRapidTrigger(self, trigger_cidx):
        res = self.construct_and_process_request(function_nb=8, params=[trigger_cidx, 0, 0])
        return res

    # [9] getMultiAction(trigger_cidx) → trigger_cidx, actuation_point_hi, actuation_point_lo, assignment, actuationEvent
    def getMultiAction(self, trigger_cidx):
        res = self.construct_and_process_request(function_nb=9, params=[trigger_cidx, 0, 0])
        return res

    # [10] getCombineThresholdTrigger(trigger_cidx) → trigger_cidx, combine_cidx, actuation_point

"""     # [11] setAnalogGlobalStatus(status)
    def setAnalogGlobalStatus(self, status):
        res = self.construct_and_process_request(function_nb=11, params=[status, 0, 0])
        return res

    # [12] getAnalogGlobalStatus() → status
    def getAnalogGlobalStatus(self):
        res = self.construct_and_process_request(function_nb=12, params=[0, 0, 0])
        return res

    # [13] setAssignGlobalStatus(status)
    def setAssignGlobalStatus(self, status):
        res = self.construct_and_process_request(function_nb=13, params=[status, 0, 0])
        return res

    # [14] getAssignGlobalStatus() → status
    def getAssignGlobalStatus(self):
        res = self.construct_and_process_request(function_nb=14, params=[0, 0, 0])
        return res """