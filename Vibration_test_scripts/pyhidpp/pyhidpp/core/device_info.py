from dataclasses import field
from .feature_info import FeatureInfo

from .interface import HIDPPInterface
from .logger import get_pyhidpp_logger

from .fw_info import DeviceInfoStruct, FirmwareInfo


class DeviceInfo:
    """
    Handles device information, feature index mapping, FW entities enumeration, pretty print
    """

    name: str
    vid: int
    pid: int
    tid: int
    features: dict[int, FeatureInfo]
    sub_idx: int
    dev_type: str | None
    link: int | None
    entity_cnt: int
    unit_id: int
    transport: int
    modeId: list[int]
    capabilities: int
    entities: list[FirmwareInfo]

    def __init__(
        self, vid, pid, interface: HIDPPInterface, name, sub_idx, dev_type=None, link=None
    ):
        self.logger = get_pyhidpp_logger()
        self.interface = interface
        self.name = name
        self.sub_idx = sub_idx
        self.link = link
        self.vid = vid
        self.pid = pid
        self.dev_type = dev_type
        self.tid = None  # need to connect and read app entity transport id

        self.features = {}
        self.entities = []
        # feature 0 always in idx 0
        self.add_feature(FeatureInfo(0, 0, False, False, 0))

    def add_entity_fw_info(self, entity: FirmwareInfo):
        self.entities.append(entity)

    def add_feature(self, feature_info: FeatureInfo):
        self.features[feature_info.id] = feature_info

    def print_device_info(self):
        self.logger.info("Device info:")
        self.logger.info("Entity cnt: {}".format(self.entity_cnt))
        self.logger.info("unitId: {}".format(self.unit_id))
        self.logger.info("transport: {}".format(self.transport))
        self.logger.info("modeId: {}".format(self.modeId))
        self.logger.info("capabilities: {}".format(self.capabilities))
        self.logger.info(
            "VID: {:04X}, PID: {:04X}, TID: {:04X}".format(self.vid, self.pid, self.tid)
        )

        for entity in self.entities:
            self.logger.info(
                f"Entity idx:{entity.entity_idx} type:{entity.dev_type}, fwName:{entity.fw_name}, "
                f"rev:{entity.rev}, build:{entity.build:04X}, trPid:{entity.trPid:04X}, "
                f"active:{entity.active}"
            )

    def print_features_set(self):
        for feature, info in self.features.items():
            self.logger.info(
                "idx:id {}:0x{:04X} - eng:{}, obsolete:{}, version:{}".format(
                    info.idx,
                    feature,
                    info.eng,
                    info.obsolete,
                    info.version,
                )
            )

    def set_device_info(self, data: DeviceInfoStruct):
        self.capabilities = data.capabilities
        self.modeId = data.mode_id
        self.transport = data.transport
        self.entity_cnt = data.entity_count
        self.unit_id = data.unit_id

    def is_enumerated(self, feature_id):
        if feature_id in self.features:
            return True
        return False

    def __repr__(self) -> str:
        return (
            f"HIDPPDevice(name={self.name}, vid={self.vid:04X}, pid={self.pid:04X},"
            f" sub_idx={self.sub_idx}, type={self.dev_type}, link={'ON' if self.link == 0 else 'OFF' if self.link == 1 else 'Unknown'})"
        )
