import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections.abc import Callable

from .bitstream import BitstreamVersion
from .register import Register


class Sensor(ABC):
    bitstream_progress_callback: Callable[[float], None] | None
    image_dump_callback: Callable[[list[float]], None] | None
    image_dump_progress_callback: Callable[[float], None] | None
    bitstream_version: BitstreamVersion
    bistream_start_addr: int
    bitstream_version_addr: int
    bitstream_build_addr: int | None
    bitstream_variant_addr: int | None
    reg: dict[str, Register]

    def __init__(self, interface):
        self.name = "generic sensor"
        self.interface = interface
        self.read_mask = 0x80
        self.write_mask = 0x00
        self.idle_byte = 0x80
        self.log = logging.getLogger("pyranus")

        self.bitstream_progress_callback = None
        self.image_dump_callback = None
        self.image_dump_progress_callback = None
        self.control1_value = None

    def __post_init__(self):
        self.detect_state()
        self.read_bitstream_version()

    def set_bitstream_callback(self, callback):
        self.bitstream_progress_callback = callback

    def set_image_callback(self, progress, data):
        self.image_dump_progress_callback = progress
        self.image_dump_callback = data

    def detect_state(self):
        return self.interface.detect_state()

    def cs_enable(self):
        return self.interface.cs_enable()

    def cs_disable(self):
        return self.interface.cs_disable()

    def fw_stop(self):
        return self.interface.fw_stop()

    def fw_resume(self):
        if self.control1_value:
            self.write_register("Control1", self.control1_value)
        return self.interface.fw_resume()

    def transmission(self, sdo):
        return self.interface.transmission(sdo)

    @staticmethod
    def is_register_address(ref):
        try:
            val = int(ref, 16)
            return val < 0xFF
        except ValueError:
            return False

    def get_register(self, ref: str | int | Register) -> Register | None:
        dic_reg = None
        if Sensor.is_register_address(ref):
            match = [reg for reg in self.reg.values() if reg.address == int(ref, 16)]
            if len(match) > 0:
                dic_reg = match[0]
            else:
                dic_reg = Register("unknown", int(ref, 16), 1, [0])
        elif type(ref) == str and ref in self.regs:
            dic_reg = self.regs[ref]
        elif type(ref) == Register:
            dic_reg = ref
        return dic_reg

    def read_register(self, reg):
        dic_reg = self.get_register(reg)
        if dic_reg is not None:
            sdi = self.transmission(
                [address | self.read_mask for address in dic_reg.address]
                + [self.idle_byte]
            )
            value = 0
            for i in range(dic_reg.size):
                value *= 256
                value += sdi[i + 1]
            return value
        else:
            self.log.debug(f"Error: {reg} not well formated")

    def write_non_adf_register(self, reg, val):
        self.cs_enable()
        self.control1_value = self.read_register("Control1")
        self.write_register("Control1", 0x00)
        self.write_register("Reset", 0xB0)
        self.cs_disable()

        self.cs_enable()
        self.write_register(reg, val)
        self.write_register("Control1", self.control1_value)
        self.cs_disable()

    def write_register(self, reg, val):
        dic_reg = self.get_register(reg)
        if dic_reg:
            val_bytes = [
                (val >> (8 * i)) & 0xFF for i in range(dic_reg.size - 1, -1, -1)
            ]
            sdo = [
                f(i)
                for i in range(dic_reg.size)
                for f in (
                    lambda x: (dic_reg.address[x] | self.write_mask),
                    lambda x: val_bytes[x],
                )
            ] + [self.idle_byte]
            sdi = self.transmission(sdo)
            value = 0
            for i in range(dic_reg.size):
                value *= 256
                value += sdi[i + 1]
            return value
        else:
            self.log.debug(f"Error: {reg} not well formated")
        self.transmission([reg | self.write_mask, val])

    def read_registers(self, reg_list):
        ans = []
        max_length = 14
        size = 0
        size_list = []
        addr_list = []
        for reg in reg_list:
            dic_reg = self.get_register(reg)
            if dic_reg is None:
                self.log.debug(f"Error: {reg} not well formated")
                return None

            if size + dic_reg.size > max_length:
                sdi = self.transmission(addr_list + [self.idle_byte])
                if sdi:
                    offset = 1
                    for size in size_list:
                        value = 0
                        for i in range(size):
                            value *= 256
                            value += sdi[i + offset]
                        offset += size
                        ans.append(value)
                size = 0
                size_list = []
                addr_list = []
            addr_list.extend([address | self.read_mask for address in dic_reg.address])
            size_list.append(dic_reg.size)
            size += dic_reg.size

        sdi = self.transmission(addr_list + [self.idle_byte])
        if sdi:
            offset = 1
            for size in size_list:
                value = 0
                for i in range(size):
                    value *= 256
                    value += sdi[i + offset]
                offset += size
                ans.append(value)
        return ans

    def read_bitstream_version(self) -> BitstreamVersion:
        self.cs_enable()
        addr = self.bistream_start_addr + self.bitstream_version_addr
        sdi = self.transmission(
            [
                0x2A,
                0xCF,
                0x2B,
                0x02,
                0x2C,
                addr >> 8,
                0x2D,
                addr & 0xFF,
                0xAE,
                0xAF,
                0x80,
                0x2A,
                0x00,
            ]
        )
        major = sdi[9]
        minor = sdi[10]
        if self.bitstream_build_addr is None:
            build = None
        else:
            addr = self.bistream_start_addr + self.bitstream_build_addr
            sdi = self.transmission(
                [
                    0x2A,
                    0xCF,
                    0x2B,
                    0x02,
                    0x2C,
                    addr >> 8,
                    0x2D,
                    addr & 0xFF,
                    0xAE,
                    0xAF,
                    0x80,
                    0x2A,
                    0x00,
                ]
            )
            build = sdi[9] * 256 + sdi[10]
        if self.bitstream_variant_addr is None:
            variant = None
        else:
            addr = self.bistream_start_addr + self.bitstream_variant_addr
            sdi = self.transmission(
                [
                    0x2A,
                    0xCF,
                    0x2B,
                    0x02,
                    0x2C,
                    addr >> 8,
                    0x2D,
                    addr & 0xFF,
                    0xAE,
                    0xAF,
                    0x80,
                    0x2A,
                    0x00,
                ]
            )
            variant = sdi[9] * 256 + sdi[10]
        self.cs_disable()
        self.bitstream_version = BitstreamVersion(major, minor, build, variant)

        return self.bitstream_version

    def load_bitstream(self, bitstream):
        self.fw_stop()
        self.cs_enable()
        control1_value = self.read_register("Control1")
        self.write_register("Control1", 0)
        self.enable_bitstream_upload()

        # Upload the bitstream 6 bytes by 6 bytes, then upload the rest 2 bytes by 2 bytes
        step = 6
        i = 0
        for b in zip(*[bitstream.bytes[i::step] for i in range(step)]):
            self.transmission(
                [0x2E, b[0], 0x2F, b[1], 0x2E, b[2], 0x2F, b[3], 0x2E, b[4], 0x2F, b[5]]
            )
            i += step
            if callable(self.bitstream_progress_callback):
                self.bitstream_progress_callback(i * 100 // len(bitstream.bytes))
        if len(bitstream.bytes) % step != 0:
            offset = len(bitstream.bytes) - (len(bitstream.bytes) % step)
            for b in zip(*[bitstream.bytes[offset + i :: step] for i in range(2)]):
                self.transmission([0x2E, b[0], 0x2F, b[1]])
                i += 2
                if callable(self.bitstream_progress_callback):
                    self.bitstream_progress_callback(i * 100 // len(bitstream.bytes))

        self.transmission([0x2A, 0x00])  # DISABLING CONTROL RAM ACCESS
        self.write_register("Control1", control1_value)
        self.cs_disable()
        self.read_bitstream_version()
        self.fw_resume()

    def end_image_dump(self):
        """common end of image dump routine"""
        self.cs_enable()
        self.write_register("Control1", self.control1_value)
        self.cs_disable()
        if callable(self.image_dump_progress_callback):
            self.image_dump_progress_callback(100)
        if callable(self.image_dump_callback):
            self.image_dump_callback(self.dumped_image)

    def enable_bitstream_upload(self):
        pass

    def close(self):
        self.cs_enable()
        # better to put a mouse reset here instead
        self.write_register("Reset", 0x80)
        self.cs_disable()
        self.fw_resume()
