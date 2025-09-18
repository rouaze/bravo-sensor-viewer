from ..core.fw_info import DeviceInfoStruct, FirmwareInfo
from .feature import Feature
from ..core.utils import list_to_u32_be, list_to_u16_be


class X0003(Feature):
    feature_id = 0x0003

    def get_device_info(self) -> DeviceInfoStruct:
        params = [0x00] * 3
        res = self.construct_and_process_request(function_nb=0, params=params)

        if res is None:
            self.logger.warning("x0003_getDeviceInfo response none")
            return None

        entityCnt = res.params[0]
        unitId = list_to_u32_be(res.params[1:5])
        transport = list_to_u16_be(res.params[5:7])
        modeId = res.params[7:13]
        capabilities = res.params[14]

        return DeviceInfoStruct(entityCnt, unitId, transport, modeId, capabilities)

    def get_fw_info(self, entity_idx: int):
        params = [0x00] * 3
        params[0] = entity_idx
        res = self.construct_and_process_request(function_nb=1, params=params)

        if res is None:
            self.logger.warning("x0003_getFwInfo response none")
            return None

        dev_type = res.params[0]
        fwName = (
            chr(res.params[1])
            + chr(res.params[2])
            + chr(res.params[3])
            + str(res.params[4] >> 4)
            + str(res.params[4] & 0x0F)
        )
        rev = res.params[5]
        build = int("".join([hex(p)[2:] for p in res.params[6:8]]))
        active = bool(res.params[8] & 0x01)
        trPid = list_to_u16_be(res.params[9:11])

        return FirmwareInfo(entity_idx, dev_type, fwName, rev, build, trPid, active)

    def get_device_serial_number(self):
        params = [0x00] * 3
        res = self.construct_and_process_request(function_nb=2, params=params)

        if res is None:
            self.logger.warning("x0003_getDeviceSerialNumber response none")
            return None

        serial_number = ''.join(chr(char) for char in res.params[:12])
        
        return serial_number
    