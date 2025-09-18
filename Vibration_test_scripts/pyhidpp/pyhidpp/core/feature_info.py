from dataclasses import dataclass


@dataclass
class FeatureInfo:
    id: int
    idx: int
    obsolete: bool
    eng: bool
    version: int
