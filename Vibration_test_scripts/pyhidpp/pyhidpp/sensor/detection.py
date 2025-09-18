from .em7792 import Em7792
from .em7790 import Em7790
from .em7795 import Em7795
from .em7788 import Em7788
from .sensor import Sensor

sensor_id = {0x95: Em7795, 0x90: Em7790, 0x88: Em7788, 0x92: Em7792}


def sensor_autodetect(interface) -> Sensor | None:
    sdi = interface.transmission([0x80, 0x80])
    return (
        sensor_id[sdi[1]](interface)
        if ((sdi is not None) and (sdi[1] in sensor_id))
        else None
    )
