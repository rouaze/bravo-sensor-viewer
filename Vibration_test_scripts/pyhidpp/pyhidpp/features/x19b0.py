from .feature import Feature

class X19B0(Feature): # Haptic feature
    feature_id = 0x19B0

    
    # [0] getCapabilities() → Capabilities, supportedHapticLevels, defaultLevel, hapticWaveformList
    def getCapabilities(self):
            res = self.construct_and_process_request(function_nb=0, params=[])
            return res

    # [1] getHapticConfig() → configuration, currentHapticLevel
    def getHapticConfig(self):
            res = self.construct_and_process_request(function_nb=1, params=[])
            return res
    
    # [2] setHapticConfig(configuration, currentHapticLevel) → configuration, currentHapticLevel
    def setHapticConfig(self, configuration, currentHapticLevel):
            payload = [configuration, currentHapticLevel]
            res = self.construct_and_process_request(function_nb=2, params=payload)
            return res
    
    # [3] getHapticInfo() → hapticStatus
    def getHapticInfo(self):
            res = self.construct_and_process_request(function_nb=3, params=[])
            return res
    
    # [4] playHapticWaveform(hapticWaveformID) → hapticWaveformID, waveformStatus
    def playHapticWaveform(self, hapticWaveformID):
            payload = [hapticWaveformID]
            res = self.construct_and_process_request(function_nb=4, params=payload)
            return res

    # [event0] hapticInfoEvent() → hapticStatus
    # Not implemented