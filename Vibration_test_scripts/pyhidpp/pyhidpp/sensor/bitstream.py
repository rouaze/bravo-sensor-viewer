from dataclasses import dataclass


@dataclass
class BitstreamVersion:
    major: int
    minor: int
    build: int | None = None
    variant: int | None = None

    def __str__(self) -> str:
        bitstream_str = f"{self.major}.{self.minor}"
        if self.build is not None:
            bitstream_str += f".{self.build}"
        if self.variant is not None:
            bitstream_str += f".{self.variant}"
        return bitstream_str
