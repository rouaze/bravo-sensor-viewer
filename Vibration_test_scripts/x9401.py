from pyhidpp.pyhidpp import Feature
from enum import Enum

class X9401(Feature):
    feature_id = 0x9401
    def getCapabilities(self):
        res = self.construct_and_process_request(0, [0])
        
        return res

    def diagnosticTest(self,LRA_ERM, FB_BRAKE_FACTOR, LOOP_GAIN, RATED_VOLTAGE, OD_CLAMP, AUTO_CAL_TIME, DRIVE_TIME, SAMPLE_TIME, BLANKING_TIME, IDISS_TIME, ZC_DET_TIME):
        res = self.construct_and_process_request(1, [FB_BRAKE_FACTOR, LOOP_GAIN, RATED_VOLTAGE, OD_CLAMP, AUTO_CAL_TIME, DRIVE_TIME, SAMPLE_TIME, BLANKING_TIME, IDISS_TIME, ZC_DET_TIME])
        
        return res

    def playWaveform(self,waveformID, level=50):

        res = self.construct_and_process_request(4, [waveformID, level])
        return res


# %%
# Test
if __name__ == '__main__':    # called as a script
    pass
    """ import sys
    from pathlib import Path
    project_path = str(Path(__file__).parent.parent.parent.parent.parent)
    if project_path not in sys.path:
        sys.path.append(project_path)
    from common.wheel.hidpp_wheel import HidppWheel
    from common.pyhidpp.pyhidpp.features.x92d1 import X92D1

    logiwheel = HidppWheel()

    logiwheel.wheel.features.x92D1.start_moving(4000, 100, 360, 0, X92D1.Mode.Normal, X92D1.Flags.NoFlags)

    logiwheel.close() """

 # %%