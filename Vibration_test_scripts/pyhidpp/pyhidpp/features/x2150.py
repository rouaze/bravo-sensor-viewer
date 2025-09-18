from .feature import Feature

class X2150(Feature): # Thumbwheel
    feature_id = 0x2150
    
    # [0] getThumbwheelInfo() → info, capabilities
    def getThumbwheelInfo(self):
            res = self.construct_and_process_request(function_nb=0, params=[])
            return res

    # [1] getThumbwheelStatus() → reporting mode, inv_dir, touch, proxy
    def getThumbwheelStatus(self):
            res = self.construct_and_process_request(function_nb=1, params=[])
            return res
    
    # [2] setThumbwheelReporting(reporting mode, inv_dir)
    def setThumbwheelReporting(self, reporting_mode, inv_dir):
            payload = [reporting_mode, inv_dir]
            res = self.construct_and_process_request(function_nb=2, params=payload)
            return res
    
    # [event0] thumbwheelEvent() → rotation, time stamp, rotation status, touch, proxy, single tap
    
