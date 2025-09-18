class HIDPPInterface:
    """
    HIDPP Interface definition
    """

    def __init__(self, short=None, long=None, extra_long=None):
        self.short = short
        self.long = long
        self.extra_long = extra_long

    def has_short(self):
        return self.short is not None

    def has_long(self):
        return self.long is not None

    def has_xl(self):
        return self.extra_long is not None

    # def __str__(self) -> str:
    #     return f"HIDPPInterface({self.short},{self.long},{self.extra_long})"

    def endpoint_repr(self, endpoint) -> str:
        if endpoint is None:
            return "None"
        return f"{{vid={endpoint['vendor_id']:04X}, pid={endpoint['product_id']:04X}}}"

    def __repr__(self) -> str:
        return f"HIDPPInterface(short={self.endpoint_repr(self.short)},long={self.endpoint_repr(self.long)},xlong={self.endpoint_repr(self.extra_long)})"
