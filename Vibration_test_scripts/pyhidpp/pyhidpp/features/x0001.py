from ..core.feature_info import FeatureInfo
from .feature import Feature


class X0001(Feature):
    feature_id = 0x0001

    def get_count(self):
        res = self.construct_and_process_request(function_nb=0, params=[0, 0, 0])

        cnt = 0
        if res is not None:
            cnt = res.params[0]
        return cnt

    def get_feature_id(self, feature_idx) -> FeatureInfo:
        res = self.construct_and_process_request(
            function_nb=1, params=[feature_idx, 0, 0]
        )

        f_id = 0
        obsolete = False
        eng = False
        version = 0
        if res is not None:
            f_id = res.params[0] << 8 | res.params[1]
            obsolete = bool((res.params[2] >> 7) & 0x01)
            eng = bool((res.params[2] >> 5) & 0x01)
            version = res.params[3]
        else:
            self.logger.warning("No response for Feature index {}d".format(f_id))
        return FeatureInfo(f_id, feature_idx, obsolete, eng, version)
