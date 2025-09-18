from dataclasses import dataclass
from enum import IntEnum

from .feature import Feature


class ChargingStatus(IntEnum):
    DISCHARGING = 0
    CHARGING = 1
    CHARGING_SLOW = 2
    CHARGE_COMPLETE = 3
    CHARGE_ERROR = 4


class BatteryLevel(IntEnum):
    CRITICAL = 1
    LOW = 2
    GOOD = 4
    FULL = 8


@dataclass
class X1004State:
    state_of_charge: int | None = None
    battery_level: BatteryLevel | None = None
    charging_status: ChargingStatus | None = None
    external_power_status: int | None = None
    fast_charging: int | None = None
    removable_battery_status: int | None = None


class X1004(Feature):
    feature_id = 0x1004

    def get_status(self, version: int = 5) -> X1004State | None:
        res = self.construct_and_process_request(function_nb=1, params=[])
        if res:
            state = X1004State()
            if version >= 5:
                state.removable_battery_status = res.params[5]
            if version >= 4:
                state.fast_charging = res.params[4]

            state.state_of_charge = res.params[0]
            state.battery_level = BatteryLevel(res.params[1])
            state.charging_status = ChargingStatus(res.params[2])
            state.external_power_status = res.params[3]
            return state
