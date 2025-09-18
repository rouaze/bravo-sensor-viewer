from pyhidpp import Feature
from pyhidpp.core.devices_manager import DevicesManager


class X1234(Feature):
    feature_id = 0x1234

    def get_my_super_feature(self, custom_param: int):
        res = self.construct_and_process_request(1, [custom_param])
        return res.params[0]


dev_manager = DevicesManager()
mouse = dev_manager.connect_with_name("My Mouse")
custom_feature = X1234(mouse)
custom_val = custom_feature.get_my_super_feature(100)
