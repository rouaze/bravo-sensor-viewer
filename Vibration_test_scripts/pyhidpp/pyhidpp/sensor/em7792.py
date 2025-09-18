from .image import ImageCalibration
from .register import Register
from .sensor import Sensor
import numpy as np


class Em7792(Sensor):
    def __init__(self, interface):
        Sensor.__init__(self, interface)
        self.name = "Pluto"
        self.dumped_image = None
        self.width = 16
        self.height = 16
        self.bistream_start_addr = 0x0
        self.bitstream_version_addr = 0xBFF
        self.bitstream_build_addr = None
        self.bitstream_variant_addr = None
        self.image_calibration = None
        self.regs_list = [
            Register("ProductID", [0x00], "R"),
            Register("RevisionID", [0x01], "R"),
            Register("Control", [0x02], "RW", 0x00),
            Register("Status", [0x04], "R", 0x10),
            Register("DeltaX", [0x05], "R"),
            Register("DeltaY", [0x06], "R"),
            Register("DeltaH", [0x07], "R"),
            Register("SPIConfig", [0x09], "RW", 0x00),
            Register("Reset", [0x0A], "RW"),
            Register("ServReq", [0x0B], "RW", 0x00),
            Register("ResPgmX", [0x0C], "RW", 0x1F),
            Register("ResPgmY", [0x0D], "RW", 0x1F),
            Register("Rescale", [0x0E], "RW", 0x10),
            Register("DCDCCtrl", [0x0F], "RW"),
            Register("IntegTime", [0x10], "R", 0x00),
            Register("LED", [0x11], "R"),
            Register("FlashRate", [0x12, 0x13], "R"),
            Register("SFMax", [0x14], "R"),
            Register("CompSet", [0x15], "R"),
            Register("LiftStat", [0x16], "R"),
            Register("NoEdgeCntX", [0x17], "R"),
            Register("NoEdgeCntY", [0x18], "R"),
            Register("InvEdgeCntX", [0x19], "R"),
            Register("InvEdgeCntY", [0x1A], "R"),
            Register("Rest1Frate", [0x20], "RW"),
            Register("Rest2Frate", [0x21], "RW"),
            Register("Rest1-2Time", [0x22], "RW"),
            Register("Rest-STime", [0x23], "RW"),
            Register("PwrMaxFrate", [0x24], "RW"),
            Register("ResCorX", [0x25], "RW"),
            Register("ResCorY", [0x26], "RW"),
            Register("LiftMask", [0x27], "RW"),
            Register("Dtarget", [0x28], "RW"),
            Register("DDMax", [0x29], "RW"),
            Register("Rest2ExitTh", [0x3D], "RW"),
            Register("AccumClrTh", [0x1F], "RW"),
            Register("PixVoltageTrim", [0x30], "RW"),
            Register("PixCurTrim", [0x31], "RW"),
            Register("OscTrim1", [0x32], "RW"),
            Register("OscTrim2", [0x33], "RW"),
            Register("OscTrim3", [0x34], "RW"),
            Register("LEDTrim", [0x35], "RW"),
            Register("DCDCTrim", [0x36], "RW"),
            Register("FixIntegTime", [0x60], "RW"),
            Register("FixLEDSpat", [0x61], "RW"),
            Register("FixFlashRate", [0x62, 0x63], "RW"),
            Register("FixSFMax", [0x64], "RW"),
            Register("FixCompSet", [0x65], "RW"),
            Register("PixelDump", [0x66], "RW"),
            Register("PixCol", [0x67], "RW"),
            Register("PixRow", [0x68], "RW"),
            Register("RTE0_h", [0x69], "RW"),
            Register("RTE1_h", [0x6A], "RW"),
            Register("RTE0_l", [0x6C], "RW"),
            Register("RTE1_l", [0x6D], "RW"),
            Register("PixelSel", [0x70], "RWU"),
            Register("PixelOut", [0x71, 0x72], "R"),
            Register("TestPads", [0x75], "RW"),
            Register("TestPassword", [0x76], "RW"),
            Register("TestSelect", [0x77], "RW"),
            Register("TestOscillator", [0x78], "RW"),
            Register("TestMode1", [0x79], "RW"),
            Register("TestMode2", [0x7A], "RW"),
            Register("TestMode3", [0x7B], "RW"),
            Register("ClkReg", [0x7C], "RW"),
            Register("DCDCTest", [0x7D], "RW"),
        ]
        self.regs = {}
        for reg in self.regs_list:
            self.regs[reg.name] = reg

        self.__post_init__()

    def ad_calibration(self):
        self.write_register("Control", 0x00)
        self.write_register("TestPassword", 0x88)
        self.write_register("FixIntegTime", 0x14)
        self.write_register("TestSelect", 0x40)

        # 100mV calibration source
        self.write_register("PixelDump", 0x85)
        self.write_register("Control", 0x05)
        c_100 = self.read_registers(["PixelOut"] * self.height)

        # 500mV calibration source
        self.write_register("PixelDump", 0x89)
        self.write_register("Control", 0x05)
        c_500 = self.read_registers(["PixelOut"] * self.height)

        # select static pixel column mode (no comparator triggering)
        self.write_register("PixelDump", 0x80)

        self.image_calibration = ImageCalibration(np.array(c_100), np.array(c_500))

    def manual_image_dump(self):
        self.dumped_image = np.zeros((self.width, self.height))
        self.fw_stop()
        self.cs_enable()
        # save the previous register value
        self.control1_value = self.read_register("Control")

        # ad calibration if not done before
        if self.image_calibration is None:
            self.ad_calibration()

        # Stop continuous flashing before image dump
        self.write_register("Control", 0x00)
        self.write_register("TestSelect", 0x00)
        self.cs_disable()
        self.cs_enable()
        for i in range(self.width):
            self.write_register("PixCol", i)
            self.write_register("Control", 0x05)
            while self.read_register("Control") & 0x01:
                pass
            self.write_register("PixelSel", 0x00)
            pixels = self.read_registers(["PixelOut"] * self.height)  # second loop here
            self.dumped_image[i, :] = pixels
            # self.dumped_image.extend(pixels)
            if callable(self.image_dump_progress_callback):
                self.image_dump_progress_callback(i * 100 // self.width)

        self.dumped_image = self.dumped_image * self.image_calibration.k.reshape(
            (self.width, 1)
        ) + self.image_calibration.q.reshape((self.width, 1))
        self.dumped_image = list(self.dumped_image.flatten("F"))
        self.write_register("Reset", 0xB8)

        self.cs_disable()

        self.cs_enable()
        self.write_register("Control", self.control1_value)
        self.cs_disable()
        if callable(self.image_dump_progress_callback):
            self.image_dump_progress_callback(100)
        if callable(self.image_dump_callback):
            self.image_dump_callback(self.dumped_image)

        return self.dumped_image
