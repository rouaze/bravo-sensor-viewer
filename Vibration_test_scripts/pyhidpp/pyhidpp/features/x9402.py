from .feature import Feature
from enum import Enum

class X9402(Feature):
    feature_id = 0x9402

    def read_measurement(self, custom_param: int=0):
        # Enhanced debugging for reconnection issues
        print(f"🔍 X9402.read_measurement called with param: {custom_param}")
        print(f"  Device connected: {self.hidpp.connected}")
        print(f"  Feature 0x9402 enumerated: {self.hidpp.device_info.is_enumerated(0x9402)}")
        
        if self.hidpp.device_info.is_enumerated(0x9402):
            feature_info = self.hidpp.device_info.features[0x9402]
            print(f"  Feature index: {feature_info.idx}")
        
        res = self.construct_and_process_request(2, [custom_param])
        print(f"  construct_and_process_request result: {res}")
        
        if res is None:
            print("ERROR: Feature 0x9402 not available on this device (sensor not supported)")
            return None
        
        if not hasattr(res, 'params') or len(res.params) < 6:
            print(f"ERROR: Invalid sensor response - expected 6+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            val = res.params[1] + res.params[2]*2**8
            if val > 2048:
                val = val - 65535
            bl = res.params[3] + res.params[4]*2**8
            if bl > 2048:
                bl = bl - 65535
            preload = res.params[5]

            if preload > 128:
                preload = (preload - 256 + 16)*-1

            return (val,bl,preload)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse sensor data: {e}")
            return None

    def monitor_mode(self, custom_param: int):
        hi_byte= (0xFF00 & custom_param)>>8
        lo_byte= (0x00FF & custom_param)
        res = self.construct_and_process_request(5, [0,lo_byte,hi_byte])
        #val = res.params[1] + res.params[2]*2**8
        return res
    def write_cal_data(self, th):
        th_low = int(th*0.8)
        th_high = int(th*1.2)
        
        th = int(th)
        th_lsb = th & 0x00FF
        th_msb = th >> 8 
        
        thl_lsb = th_low & 0x00FF
        thl_msb = th >> 8 
        
        thh_lsb = th_high & 0x00FF
        thh_msb = th >> 8 
        
        res = self.construct_and_process_request(3, [0,th_lsb,th_msb,thl_lsb,thl_msb,thh_lsb,thh_msb])
        return res
    def read_cal_data(self, custom_param: int):
        res = self.construct_and_process_request(4,[custom_param])
        if res is None:
            print("ERROR: Feature 0x9402 calibration not available on this device")
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 7:
            print(f"ERROR: Invalid calibration response - expected 7+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            nom_th = (res.params[2]>>8) + res.params[1]
            low_th = (res.params[4]>>8) + res.params[3]
            high_th = (res.params[6]>>8) + res.params[5]

            return (nom_th,low_th,high_th)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse calibration data: {e}")
            return None

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