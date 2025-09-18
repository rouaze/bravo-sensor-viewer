import threading
from enum import Enum
from .feature import Feature

class X8128(Feature):
    feature_id = 0x8128
    calibrationCompleteEvent = 0

    class Status(Enum):
        Fail           = 0x00
        Success        = 0x01
    
    calibrationComplete_event = threading.Event()
    calibrationStatus = Status.Fail

    def start_calibration(self):

        self.calibrationComplete_event.clear()
        self.hidpp.register_notif(self.feature_id, self.calibrationCompleteEvent, self.calibrationCompleteCallback)

        self.construct_and_process_request(function_nb=0, params=[])
        self.calibrationComplete_event.wait()

        return self.calibrationStatus
    
    def is_calibrated(self):
        res = self.construct_and_process_request(function_nb=1, params=[])
        
        if res is None:
            return None

        return res.params[0]

    @staticmethod
    def calibrationCompleteCallback(request, timestamp):
        X8128.calibrationStatus = X8128.Status(request.params[0])
        X8128.calibrationComplete_event.set()
        return None
    
# %%
# Test
if __name__ == '__main__':    # called as a script
    import sys
    from pathlib import Path
    project_path = str(Path(__file__).parent.parent.parent.parent.parent)
    if project_path not in sys.path:
        sys.path.append(project_path)
    from common.wheel.hidpp_wheel import HidppWheel
    from common.pyhidpp.pyhidpp.features.x8128 import X8128

    logiwheel = HidppWheel()

    status = logiwheel.wheel.features.x8128.start_calibration()
    print(status.name)

    logiwheel.close()
# %%
