"""
address should be a list of register addresses in Big Endian format
"""


class Register:
    name: str
    address: list[int]
    access: str = "RW"
    default: int = None

    def __init__(self, name: str, address: list[int], access: str = "RW", default: int = None):
        self.name = name
        self.address = address
        self.access = access
        self.default = default
        self.size = len(self.address)
