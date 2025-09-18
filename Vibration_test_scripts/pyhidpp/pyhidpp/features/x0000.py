from .feature import Feature
from ..core.feature_info import FeatureInfo


class X0000(Feature):
    feature_id = 0x0000

    def get_feature(self, feature_id) -> FeatureInfo:
        params = [0x00] * 3
        params[0] = (feature_id >> 8) & 0xFF
        params[1] = feature_id & 0xFF

        res = self.construct_and_process_request(function_nb=0, params=params)

        f_idx = 0
        obsolete = False
        eng = False
        version = 0
        if res is not None:
            f_idx = res.params[0]
            if f_idx != 0:  # idx 0 means not found
                obsolete = bool((res.params[1] >> 7) & 0x01)
                eng = bool((res.params[1] >> 5) & 0x01)
                version = res.params[2]
            else:
                self.logger.warning("Feature id {} not found".format(feature_id))
        else:
            self.logger.warning("No response for Feature id {}".format(feature_id))

        return FeatureInfo(feature_id, f_idx, obsolete, eng, version)
