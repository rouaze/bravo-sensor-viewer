from .feature import Feature
from dataclasses import dataclass


@dataclass
class X1000State:
    battery_discharge_level: int
    battery_discharge_next_level: int
    battery_status: int


class X1000(Feature):
    feature_id = 0x1000

    def get_battery_level_status(self):
        res = self.construct_and_process_request(0, [])
        if res:
            return X1000State(res.params[0], res.params[1], res.params[2])
