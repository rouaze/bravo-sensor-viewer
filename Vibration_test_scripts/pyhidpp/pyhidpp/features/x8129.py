from .feature import Feature
from enum import Enum
import struct

class X8129(Feature):
    feature_id = 0x8129

    # classes for enums

    class DriverAttributeIndex(Enum):
        Infos           = 0
        Name            = 1
        Description     = 2

    class CurveAttributeIndex(Enum):
        Type            = 0
        MinIndex        = 1
        MaxIndex        = 2
        MinValue        = 3
        MaxValue        = 4
        Name            = 5
        Description     = 6

    class CurveType(Enum):
        TNone           = 0
        Int16           = 1
        UInt16          = 2
        Int32           = 3
        UInt32          = 4
        Float           = 5
        Bool            = 6
        Int8            = 7
        UInt8           = 8

    class FunctionAttributeIndex(Enum):
        ArgCount        = 0
        Name            = 1
        Description     = 2

    class FunctionArgumentAttributeIndex(Enum):
        Type            = 0
        MinValue        = 1
        MaxValue        = 2
        Value           = 3
        DefaultValue    = 4
        Name            = 5
        Description     = 6

    # read and write private functions
    
    def _read_attribute_value(self, res, type, offset=0):
        if type == self.CurveType.TNone:
            return None
        elif type == self.CurveType.Int16:
            return struct.unpack('>h', bytes(res.params[offset:offset+2]))[0]   # int16
        elif type == self.CurveType.UInt16:
            return struct.unpack('>H', bytes(res.params[offset:offset+2]))[0]   # uint16
        elif type == self.CurveType.Int32:
            return struct.unpack('>l', bytes(res.params[offset:offset+4]))[0]   # int32
        elif type == self.CurveType.UInt32:
            return struct.unpack('>L', bytes(res.params[offset:offset+4]))[0]   # uint32
        elif type == self.CurveType.Float:
            return struct.unpack('>f', bytes(res.params[offset:offset+4]))[0]   # float32
        elif type == self.CurveType.Bool:
            return struct.unpack('>?', bytes(res.params[offset:offset+1]))[0]   # bool
        elif type == self.CurveType.Int8:
            return struct.unpack('>b', bytes(res.params[offset:offset+1]))[0]   # int8
        elif type == self.CurveType.UInt8:
            return struct.unpack('>B', bytes(res.params[offset:offset+1]))[0]   # uint8
        
    def _write_attribute_value(self, value, type):
        if type == self.CurveType.TNone:
            return None
        elif type == self.CurveType.Int16:
            return list(struct.pack('>h', value))   # int16
        elif type == self.CurveType.UInt16:
            return list(struct.pack('>H', value))   # uint16
        elif type == self.CurveType.Int32:
            return list(struct.pack('>l', value))   # int32
        elif type == self.CurveType.UInt32:
            return list(struct.pack('>L', value))   # uint32
        elif type == self.CurveType.Float:
            return list(struct.pack('>f', value))   # float32
        elif type == self.CurveType.Bool:
            return list(struct.pack('>?', value))   # bool
        elif type == self.CurveType.Int8:
            return list(struct.pack('>b', value))   # int8
        elif type == self.CurveType.UInt8:
            return list(struct.pack('>B', value))   # uint8
        
    # protocol functions

    def get_info(self):
        res = self.construct_and_process_request(function_nb=0, params=[])
        if res is None:
            self.logger.warning("get_info response none")
            return None
        return res.params[0]

    def get_driver_attribute(self, driver_index, attribute_index, offset=0):
        if driver_index is None or attribute_index is None:
            self.logger.warning("invalid parameter")
            return None
        res = self.construct_and_process_request(function_nb=1, params=[driver_index, attribute_index.value, offset])
        if res is None:
            self.logger.warning("get_driver_attribute response none")
            return None
        if attribute_index == self.DriverAttributeIndex.Infos:
            curve_count = res.params[0]
            function_count = res.params[1]
            return curve_count, function_count
        elif attribute_index in (self.DriverAttributeIndex.Name, self.DriverAttributeIndex.Description):
            return ''.join(chr(char) for char in res.params[:17])   # string
        else:
            return None

    def get_curve_attribute(self, driver_index, curve_index, attribute_index, offset=0, curve_type=0):
        if driver_index is None or curve_index is None or attribute_index is None:
            self.logger.warning("invalid parameter")
            return None, None
        res = self.construct_and_process_request(function_nb=2, params=[driver_index, curve_index, attribute_index.value, offset])
        if res is None:
            self.logger.warning("get_curve_attribute response none")
            return None
        if attribute_index == self.CurveAttributeIndex.Type:
            curve_type = self.CurveType(res.params[0])
            curve_flags = res.params[1] 
            return curve_type, curve_flags
        elif attribute_index in (self.CurveAttributeIndex.MinIndex, self.CurveAttributeIndex.MaxIndex):
            return self._read_attribute_value(res, self.CurveType.UInt32)      
        elif attribute_index in (self.CurveAttributeIndex.MinValue, self.CurveAttributeIndex.MaxValue):
            return self._read_attribute_value(res, curve_type)
        elif attribute_index in (self.CurveAttributeIndex.Name, self.CurveAttributeIndex.Description):
            return ''.join(chr(char) for char in res.params[:17])   # string
        else:
            return None

    def get_curve_point(self, driver_index, curve_index, point_index, curve_type):
        if driver_index is None or curve_index is None or point_index is None:
            self.logger.warning("invalid parameter")
            return None
        point_index_lst = self._write_attribute_value(point_index, self.CurveType.UInt32)
        res = self.construct_and_process_request(function_nb=3, params=[driver_index, curve_index] + point_index_lst)
        if res is None:
            self.logger.warning("get_curve_attribute response none")
            return None
        point_value = self._read_attribute_value(res, curve_type)
        timestamp = self._read_attribute_value(res, self.CurveType.UInt32, 4)
        return point_value, timestamp
    
    def set_curve_point(self, driver_index, curve_index, point_index, point_value, curve_type):
        if driver_index is None or curve_index is None or point_index is None or point_value is None:
            self.logger.warning("invalid parameter")
            return
        point_index_lst = self._write_attribute_value(point_index, self.CurveType.UInt32)
        point_value_lst = self._write_attribute_value(point_value, curve_type)
        self.construct_and_process_request(function_nb=4, params=[driver_index, curve_index] + point_index_lst + point_value_lst)
        return
    
    def get_function_attribute(self, driver_index, function_index, attribute_index, offset=0):
        if driver_index is None or function_index is None or attribute_index is None:
            self.logger.warning("invalid parameter")
            return None
        res = self.construct_and_process_request(function_nb=7, params=[driver_index, function_index, attribute_index.value, offset])
        if res is None:
            self.logger.warning("get_curve_attribute response none")
            return None
        if attribute_index == self.FunctionAttributeIndex.ArgCount:
            arg_count = res.params[0]
            return arg_count
        elif attribute_index in (self.FunctionAttributeIndex.Name, self.FunctionAttributeIndex.Description):
            return ''.join(chr(char) for char in res.params[:17])   # string
        else:
            return None
        
    def get_function_argument_attribute(self, driver_index, function_index, argument_index, attribute_index, offset=0, curve_type=0):
        if driver_index is None or function_index is None or argument_index is None or attribute_index is None:
            self.logger.warning("invalid parameter")
            return None
        res = self.construct_and_process_request(function_nb=8, params=[driver_index, function_index, argument_index, attribute_index.value, offset])
        if res is None:
            self.logger.warning("get_curve_attribute response none")
            return None
        if attribute_index == self.FunctionArgumentAttributeIndex.Type:
            curve_type = self.CurveType(res.params[0])
            return curve_type
        elif attribute_index in (self.FunctionArgumentAttributeIndex.MinValue, self.FunctionArgumentAttributeIndex.MaxValue, self.FunctionArgumentAttributeIndex.Value, self.FunctionArgumentAttributeIndex.DefaultValue):
            return self._read_attribute_value(res, curve_type)
        elif attribute_index in (self.FunctionArgumentAttributeIndex.Name, self.FunctionArgumentAttributeIndex.Description):
            return ''.join(chr(char) for char in res.params[:17])   # string
        else:
            return None
        
    def set_function_argument(self, driver_index, function_index, argument_index, value, curve_type):
        if driver_index is None or function_index is None or argument_index is None:
            return
        value_lst = self._write_attribute_value(value, curve_type)
        self.construct_and_process_request(function_nb=9, params=[driver_index, function_index, argument_index] + value_lst)
        return
    
    def call_function(self, driver_index, function_index):
        if driver_index is None or function_index is None:
            self.logger.warning("invalid parameter")
            return
        self.construct_and_process_request(function_nb=10, params=[driver_index, function_index])
        return      
        
    # utility functions

    def find_driver_index(self, driverName):
        driverIndex = None
        driverCount = self.get_info()

        for index in range(driverCount):
            offset = 0
            driverName2 = ""
            while True:
                driverName2 += self.get_driver_attribute(index, self.DriverAttributeIndex.Name, offset)
                offset += 1
                if driverName2.endswith('\x00') is True :
                    break    
            if driverName2.rstrip('\x00') == driverName:
                driverIndex = index
                break

        if driverIndex is None:
            self.logger.warning("unknown driver name : " + driverName)
            return None
        
        return driverIndex
        
    
    def find_curve_index(self, driverIndex, curveName):
        curveIndex = None
        curveCount, _ = self.get_driver_attribute(driverIndex, self.DriverAttributeIndex.Infos)

        for index in range(curveCount):
            offset = 0
            curveName2 = ""
            while True:
                curveName2 += self.get_curve_attribute(driverIndex, index, self.CurveAttributeIndex.Name, offset)
                offset += 1
                if curveName2.endswith('\x00') is True :
                    break  
            if curveName2.rstrip('\x00') == curveName:
                curveIndex = index
                break

        if curveIndex is None:
            self.logger.warning("unknown curve name : " + curveName)
            return None
        
        return curveIndex
    
    def find_driver_and_curve_index(self, driverName, curveName):
        curveIndex = None
        driverIndex = self.find_driver_index(driverName)
        if driverIndex is not None:
            curveIndex = self.find_curve_index(driverIndex, curveName)
        return driverIndex, curveIndex
    
    def find_function_index(self, driverIndex, functionName):
        functionIndex = None
        _, functionCount = self.get_driver_attribute(driverIndex, self.DriverAttributeIndex.Infos)

        for index in range(functionCount):
            offset = 0
            functionName2 = ""
            while True:
                functionName2 += self.get_function_attribute(driverIndex, index, self.FunctionAttributeIndex.Name, offset)
                offset += 1
                if functionName2.endswith('\x00') is True :
                    break  
            if functionName2.rstrip('\x00') == functionName:
                functionIndex = index
                break

        if functionIndex is None:
            self.logger.warning("unknown function name : " + functionName)
            return None
        
        return functionIndex
    
    def find_driver_and_function_index(self, driverName, functionName):
        functionIndex = None
        driverIndex = self.find_driver_index(driverName)
        if driverIndex is not None:
            functionIndex = self.find_function_index(driverIndex, functionName)
        return driverIndex, functionIndex

    def find_function_argument(self, driverIndex, functionIndex, argumentName):
        argumentIndex = None
        argumentCount = self.get_function_attribute(driverIndex, functionIndex, self.FunctionAttributeIndex.ArgCount)

        for index in range(argumentCount):
            offset = 0
            argumentName2 = ""
            while True:
                argumentName2 += self.get_function_argument_attribute(driverIndex, functionIndex, index, self.FunctionArgumentAttributeIndex.Name, offset)
                offset += 1
                if argumentName2.endswith('\x00') is True :
                    break
            if argumentName2.rstrip('\x00') == argumentName:
                argumentIndex = index
                break

        if argumentIndex is None:
            self.logger.warning("unknown argument name : " + argumentName)
            return None
        
        return argumentIndex
    
# %%
# Test
if __name__ == '__main__':    # called as a script
    import sys
    from pathlib import Path
    project_path = str(Path(__file__).parent.parent.parent.parent.parent)
    if project_path not in sys.path:
        sys.path.append(project_path)
    from common.wheel.hidpp_wheel import HidppWheel
    from common.pyhidpp.pyhidpp.features.x8129 import X8129

    logiwheel = HidppWheel()

    driverIndex, curveIndex = logiwheel.wheel.features.x8129.find_driver_and_curve_index("MA600", "Bias current trimming")
    if driverIndex is not None and curveIndex is not None:
        type, _ = logiwheel.wheel.features.x8129.get_curve_attribute(driverIndex, curveIndex, X8129.CurveAttributeIndex.Type)
        bct, _ = logiwheel.wheel.features.x8129.get_curve_point(driverIndex, curveIndex, 0, type)
        print("BCT: " + str(bct))

    driverIndex, curveIndex = logiwheel.wheel.features.x8129.find_driver_and_curve_index("Position", "Angular calibration.LUT")
    driverIndex = None
    if driverIndex is not None and curveIndex is not None:
        type, _ = logiwheel.wheel.features.x8129.get_curve_attribute(driverIndex, curveIndex, X8129.CurveAttributeIndex.Type)
        minIndex = logiwheel.wheel.features.x8129.get_curve_attribute(driverIndex, curveIndex, X8129.CurveAttributeIndex.MinIndex)
        maxIndex = logiwheel.wheel.features.x8129.get_curve_attribute(driverIndex, curveIndex, X8129.CurveAttributeIndex.MaxIndex)
        nbPoints = maxIndex - minIndex + 1
        lut = []
        for pointIndex in range(nbPoints):
            value, _ = logiwheel.wheel.features.x8129.get_curve_point(driverIndex, curveIndex, pointIndex, type)
            lut.append(value)
        print(lut)

    driverIndex, functionIndex = logiwheel.wheel.features.x8129.find_driver_and_function_index("Position", "Position calibration.Calibrate")
    print(driverIndex, functionIndex)

    argumentIndex = logiwheel.wheel.features.x8129.find_function_argument(driverIndex, functionIndex, "current (mA)")
    type = logiwheel.wheel.features.x8129.get_function_argument_attribute(driverIndex, functionIndex, argumentIndex, X8129.FunctionArgumentAttributeIndex.Type)
    logiwheel.wheel.features.x8129.set_function_argument(driverIndex, functionIndex, argumentIndex, 2000, type)
    argumentIndex = logiwheel.wheel.features.x8129.find_function_argument(driverIndex, functionIndex, "speed (Â°/s)")
    type = logiwheel.wheel.features.x8129.get_function_argument_attribute(driverIndex, functionIndex, argumentIndex, X8129.FunctionArgumentAttributeIndex.Type)
    logiwheel.wheel.features.x8129.set_function_argument(driverIndex, functionIndex, argumentIndex, 200, type)
    #logiwheel.wheel.features.x8129.call_function(driverIndex, functionIndex)

    logiwheel.close()

 # %%
