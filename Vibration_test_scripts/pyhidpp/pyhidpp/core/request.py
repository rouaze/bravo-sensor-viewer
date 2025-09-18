"""
HIDPP request class
"""

import logging


class HIDPPRequest:
    def __init__(
            self,
            dev_idx=0xFF,
            feature=0x00,
            function=0x00,
            sw_id=0x0F,
            params: list[int] = None,
            req_type="LONG",
            from_list: list[int] = None,
    ):
        """
        HIDPP_request constructor used to construct the hidpp request.
        construction can be done from a list (ex: from_list=[0x10 0x01 ... ])
        or can be done the different parameters (dev_idx, feature, function, sw_id, 
        params, req_type)
        """
        self.logger = logging.getLogger("hidpp")
        if from_list is not None:
            if from_list[0] == 0x10:
                # auto append '0' if needed
                from_list.extend([0] * (7 - len(from_list)))
                self.req_type = "SHORT"
                self.length = 7

            elif from_list[0] == 0x11:
                # auto append '0' if needed
                from_list.extend([0] * (20 - len(from_list)))
                self.req_type = "LONG"
                self.length = 20

            elif from_list[0] == 0x12:
                # auto append '0' if needed
                from_list.extend([0] * (64 - len(from_list)))
                self.req_type = "VERY LONG"
                self.length = 64

            else:
                self.logger.warning("ERROR: BAD REQUEST LIST FORMATTING")

            self.dev_idx = from_list[1]
            self.feature = from_list[2]
            self.function = from_list[3] >> 4
            self.sw_id = from_list[3] & 0x0F
            self.params = from_list[4:]

        else:
            self.req_type = req_type
            if req_type == "VERY LONG":
                self.length = 64
            elif req_type == "LONG":
                self.length = 20
            elif req_type == "SHORT":
                self.length = 7
            else:
                self.logger.warning("ERROR: BAD REQUEST TYPE")

            self.dev_idx = dev_idx
            self.feature = feature
            self.function = function
            self.sw_id = sw_id
            self.params = params
            while len(self.params) < self.length - 4:
                self.params.append(0)

    def build_request(self):
        """
        return the request in the form a of list ex: [0x10 0x01 ... ]
        """
        req = [0x00] * self.length
        if self.req_type == "VERY LONG":
            req[0] = 0x12
        elif self.req_type == "LONG":
            req[0] = 0x11
        elif self.req_type == "SHORT":
            req[0] = 0x10
        else:
            self.logger.warning("ERROR: BAD REQUEST TYPE")

        req[1] = self.dev_idx
        req[2] = self.feature
        req[3] = self.function << 4 | self.sw_id
        req[4:] = self.params

        return req

    def print_request_props(self):
        self.logger.info(
            "Dev idx : {}; Feature : {}; Fonction: {}; SW id : {}.".format(
                self.dev_idx, self.feature, self.function, self.sw_id
            )
        )
        self.logger.info("Params : {}.".format(self.params))
