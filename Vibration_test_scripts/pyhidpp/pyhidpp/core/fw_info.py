from dataclasses import dataclass


@dataclass
class DeviceInfoStruct:
    entity_count: int
    unit_id: int
    transport: int
    mode_id: list[int]
    capabilities: int


@dataclass
class FirmwareInfo:
    entity_idx: int
    dev_type: int
    fw_name: str
    rev: int
    build: int
    trPid: int
    active: bool
