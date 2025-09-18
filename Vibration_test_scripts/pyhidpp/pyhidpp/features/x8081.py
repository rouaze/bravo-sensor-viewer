from .feature import Feature
from ..core.utils import list_to_u32_be, list_to_u16_be, u16_to_list_be


class X8081(Feature):
    feature_id = 0x8081

    """
    WIP

    implemented:
        [1] setIndividualRgbZones(rgbIndividualZones, rgbValues) → rgbIndividualZones
        [5] setRangeRgbZones(rgbFirstZoneIDs, rgbLastZoneIDs, rgbValues) → rgbFirstZoneIDs
        [7] void frameEnd(persistence, nFramesTillNextChange)

    Not implemented
        [0] getInfo() → lightingInfo
        
        [2] setConsecutiveRgbZones(rgbZoneID[0], rgbValues) → rgbZoneID[0]
        [3] setConsecutiveRgbZonesDeltaCompression5bit(rgbZoneID[0], rgbValues) → rgbZoneID[0]
        [4] setConsecutiveRgbZonesDeltaCompression4bit(rgbZoneID[0], rgbValues) → rgbZoneID[0]
        [6] setRgbZonesSingleValue(rgbFirstZoneIDs, rgbLastZoneIDs, rgbValues) → rgbFirstZoneIDs
    """

    # [1] setIndividualRgbZones(rgbIndividualZones, rgbValues) → rgbIndividualZones
    def setIndividualRgbZones(self, rgbIndividualZones, rgbValues):
        """
            rgbValues = [ [R,G,B], [R,G,B], etc]
        """
        data = []
        for i in range(len(rgbIndividualZones)):
                data.append(rgbIndividualZones[i])
                data.extend(rgbValues[i])
        res = self.construct_and_process_request(function_nb=1, params=data)
        return None

    # [5] setRangeRgbZones(rgbFirstZoneIDs, rgbLastZoneIDs, rgbValues) → rgbFirstZoneIDs
    def setRangeRgbZones(self, rgbFirstZoneIDs, rgbLastZoneIDs, rgbValues):
        data = []
        for i in range(len(rgbFirstZoneIDs)):
                data.append(rgbFirstZoneIDs[i])
                data.append(rgbLastZoneIDs[i])
                data.extend(rgbValues[i])
        res = self.construct_and_process_request(function_nb=5, params=data)
        return None

    # [7] void frameEnd(persistence, nFramesTillNextChange)
    def frameEnd(self, persistence=0, CurrentFrame=0, nFramesTillNextChange=0):
        data = [persistence]
        data.extend(u16_to_list_be(CurrentFrame))
        data.extend(u16_to_list_be(nFramesTillNextChange))
        res = self.construct_and_process_request(function_nb=7, params=data)
        return None