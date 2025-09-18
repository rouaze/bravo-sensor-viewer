from .feature import Feature
from dataclasses import dataclass


@dataclass
class X1001State:
    battery_voltage: int
    ext_power: int
    critical: int
    slow_charge: int
    fast_charge: int
    charge_status: int


class X1001(Feature):
    feature_id = 0x1001

    def get_battery_info(self):
        res = self.construct_and_process_request(0, [])
        if res:
            return X1001State(
                res.params[0] << 0xFF + res.params[1],
                res.params[2] >> 7 & 1,
                res.params[2] >> 5 & 0b1,
                res.params[2] >> 4 & 0b1,
                res.params[2] >> 3 & 0b1,
                res.params[2] & 0b111,
            )
