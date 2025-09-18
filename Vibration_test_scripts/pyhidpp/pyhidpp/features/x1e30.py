from .feature import Feature

class X1E30(Feature): # I2C Direct Access // Need Paswword authentification (x1e00, x1602)
    feature_id = 0x1E30
    
    # [0] getNbDevices() → numberOfDevices
    def getNbDevices(self):
            res = self.construct_and_process_request(function_nb=0, params=[])
            return res

    # [1] getSelectedDevice() → deviceIdx, accessConfig
    def getSelectedDevice(self):
            res = self.construct_and_process_request(function_nb=1, params=[])
            return res
    
    # [2] selectDevice(deviceIdx, accessConfig) → deviceIdx, accessConfig
    def selectDevice(self, deviceIdx, accessConfig):
            payload = [deviceIdx, accessConfig]
            res = self.construct_and_process_request(function_nb=2, params=payload)
            return res
    
    # [3] i2cReadDirectAccess(nBytes, registerAddress) → nBytes, DataOut
    def i2cReadDirectAccess(self, nBytes, registerAddress):
            payload = [nBytes, registerAddress]
            res = self.construct_and_process_request(function_nb=3, params=payload)
            return res
    
    # [4] i2cWriteDirectAccess(nBytes, registerAddress, DataIn) → nBytes
    def i2cWriteDirectAccess(self, nBytes, registerAddress, DataIn):
            payload = [nBytes, registerAddress, DataIn]
            res = self.construct_and_process_request(function_nb=4, params=payload)
            return res

