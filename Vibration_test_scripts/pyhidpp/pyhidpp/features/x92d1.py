from .feature import Feature
from enum import Enum
from ..core.utils import u16_to_list_be

class X92D1(Feature):
    feature_id = 0x92d1

    class Mode(Enum):
        Normal          = 0
        Stop            = 1
        Loop            = 2

    class Flags(Enum):
        NoFlags         = 0x00
        StopOnStopper   = 0x01
        OpenLoop        = 0x02

    def start_moving(self, current, speed, angle, hold_time = 0, mode = Mode.Normal, flags = Flags.NoFlags):
        data = [0] * 16
        data[0:2] = u16_to_list_be(current)
        data[2:4] = u16_to_list_be(speed)
        data[4:6] = u16_to_list_be(angle)
        data[6:8] = u16_to_list_be(hold_time)
        data[8] = mode.value
        data[9] = flags.value
        self.construct_and_process_request(function_nb=0, params=data)
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
    from common.pyhidpp.pyhidpp.features.x92d1 import X92D1

    logiwheel = HidppWheel()

    logiwheel.wheel.features.x92D1.start_moving(4000, 100, 360, 0, X92D1.Mode.Normal, X92D1.Flags.NoFlags)

    logiwheel.close()

 # %%