import logging
from abc import ABC
from typing import TYPE_CHECKING

from ..core.request import HIDPPRequest
if TYPE_CHECKING:
    from ..core.connected_device import ConnectedDevice


class Feature(ABC):
    feature_id: int
    logger: logging.Logger

    def __init__(self, hidpp: "ConnectedDevice") -> None:
        self.hidpp = hidpp
        self.logger = logging.getLogger("hidpp")

    def construct_and_process_request(self, function_nb, params):
        """
        used to construct and process (send) a custom hidpp request
        defined by feature_id, function_nb, params
        """
        print(f"🔧 construct_and_process_request called for feature 0x{self.feature_id:04X}, function {function_nb}")
        
        if not self.hidpp.connected:
            print(f"  ❌ Device not connected")
            self.logger.warning("ERROR: device is not connected")
            return None
            
        dev_idx = self.hidpp.device_info.sub_idx
        print(f"  Device index: {dev_idx}")
        
        if self.hidpp.enumerate_feature(self.feature_id):
            feature_idx = self.hidpp.device_info.features[self.feature_id].idx
            print(f"  ✅ Feature enumerated, index: {feature_idx}")
        else:
            print(f"  ❌ Feature enumeration failed")
            self.logger.warning(
                "Feature id: 0x{:04X} is not available".format(self.feature_id)
            )
            return None
            
        if len(params) > 20:
            req_type = "VERY LONG"
        elif len(params) > 3:
            req_type = "LONG"
        else:
            req_type = "SHORT"
        print(f"  Request type: {req_type}, params: {params}")
            
        req = HIDPPRequest(
            dev_idx=dev_idx,
            feature=feature_idx,
            function=function_nb,
            req_type=req_type,
            params=params,
        )
        print(f"  Sending request...")
        res = self.hidpp.send_req_and_wait_response(req, timeout=1)  # Reduced from 2 to 1 second
        print(f"  Response received: {res}")
        
        if res is not None:
            print(f"    Response details: feature={res.feature}, dev_idx={res.dev_idx}, sw_id={res.sw_id}")
            print(f"    Expected: feature={feature_idx}, dev_idx={dev_idx}, sw_id={self.hidpp.sw_id}")
            
            # Check for error responses
            if res.feature == 255:  # 0xFF indicates error response
                print(f"  ❌ Device error response - code: {res.sw_id}")
                self.logger.warning(f"Device returned error response for feature 0x{self.feature_id:04X} - error code: {res.sw_id}")
                return None
                
            if (res.dev_idx == dev_idx
                and res.feature == feature_idx
                and res.sw_id == self.hidpp.sw_id):
                print(f"  ✅ Response validation passed")
                return res
            else:
                print(f"  ❌ Response validation failed")
                self.logger.warning(f"Response validation failed for feature 0x{self.feature_id:04X}")
                return None
        else:
            print(f"  ❌ No response received (timeout)")
            self.logger.warning(f"No response received for feature 0x{self.feature_id:04X}")
            return None
