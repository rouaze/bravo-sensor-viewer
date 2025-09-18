from ..core.connected_device import ConnectedDevice
import logging


class SensorInterface(ConnectedDevice):
    def __init__(self) -> None:
        self.log = logging.getLogger("hidpp")
        ConnectedDevice.__init__(self)
        self.fw_stopped = None
        self.cs_enabled = None
        self.protected = None
        self.connected = None
        self.sensor_index = None
        self.activeBuild = None
        self.init()

    def is_error(self, ans):
        return ans.feature == 0xFF

    def device_info_str(self):
        dev = self.connected_device
        if dev is not None:
            return "Device name: {}, pid: 0x{:02X}, unifying_idx: {}".format(
                dev.name, dev.pid, dev.unifying_idx
            )
        else:
            return None

    def init(self, device):
        self.enumerate_all()
        (
            entityCnt,
            unitId,
            transport,
            modeId,
            capabilities,
        ) = self.features.x0003.get_device_info()
        for entity in range(entityCnt):
            (
                dev_type,
                fwName,
                rev,
                build,
                trPid,
                active,
            ) = self.features.x0003.get_fw_info(entity)
            if active:
                self.activeBuild = build
                self
                break

    def detect_state(self):
        self.fw_stopped = None
        self.cs_enabled = None
        self.protected = None
        ans = None
        for i in range(3):
            ans = self.features.x1E00.set_enable_hidden_features(True)
            if ans is not None:
                if self.is_error(ans):
                    self.log.debug("error while enabling hidden features")
                else:
                    break
        if ans is None:
            self.connected = self.features.x0003.get_device_info() is not None
        else:
            self.connected = True
            # getSelectedDevice() → deviceIdx, accessConfig
            ans = self.features.x1E22.get_selected_device()
            if ans is not None:
                self.sensor_index = ans[0]
                self.fw_stopped = bool(ans[1])
                self.cs_enabled = bool(ans[2])

    def cs_enable(self):
        if not self.cs_enabled:
            self.features.x1E22.select_device(self.sensor_index, 0x03)
            self.cs_enabled = True

    def cs_disable(self):
        self.features.x1E22.select_device(
            self.sensor_index, 0x00 if not self.fw_stopped else 0x01
        )
        self.cs_enabled = False

    def fw_stop(self):
        self.features.x1E22.select_device(self.sensor_index, 0x01)
        self.fw_stopped = True
        self.cs_enabled = False

    def fw_resume(self):
        self.features.x1E22.select_device(self.sensor_index, 0x00)
        self.fw_stopped = False
        self.cs_enabled = False

    def transmission(self, sdo):
        if len(sdo) > 15:
            sdo = sdo[0:15]
        sdi = self.features.x1E22.spi_direct_access(len(sdo), sdo)
        # if self.transmission_log:
        #     self.transmission_log_output.print(
        #         "W: " + " ".join("{:02x}".format(x) for x in sdo)
        #     )
        #     self.transmission_log_output.print(
        #         "R: "
        #         + " ".join("{:02x}".format(x) for x in sdi.params[1 : len(sdo) + 1])
        #         if sdi
        #         else "No answer"
        #     )
        return sdi.params[1 : len(sdo) + 1] if sdi else None
