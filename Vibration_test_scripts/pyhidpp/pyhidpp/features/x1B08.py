from .feature import Feature
from ..core.utils import u16_to_list_be
import time


class X1B08(Feature):
    feature_id = 0x1b08

    # [0] getCapabilities() → analog_key_config_file_ver, analog_key_config_file_maxsize, analog_key_level_resolution
    def getCapabilities(self):
        res = self.construct_and_process_request(function_nb=0, params=[])
        return res

    # [1] getRapidTriggerState() → rapid_trigger_state
    def getRapidTriggerState(self):
        res = self.construct_and_process_request(function_nb=1, params=[])
        return res

    # [2] setRapidTriggerState(rapid_trigger_state) → rapid_trigger_state
    def setRapidTriggerState(self, state):
        res = self.construct_and_process_request(function_nb=2, params=[state, 0, 0])
        return res

    # [3] setKeyTravelEventState(key_travel_event_state) → key_travel_event_state
    def setKeyTravelEventState(self, state):
        res = self.construct_and_process_request(function_nb=3, params=[state, 0, 0])
        return res
    

        



