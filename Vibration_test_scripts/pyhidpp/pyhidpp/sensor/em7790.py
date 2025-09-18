from .sensor import Sensor
from .register import Register
from time import sleep


class Em7790(Sensor):
    def __init__(self, interface):
        Sensor.__init__(self, interface)
        self.name = "Jupiter"
        self.dumped_image = None
        self.width = 28
        self.height = 38
        self.bistream_start_addr = 0x1000
        self.bitstream_version_addr = 0xBFF
        self.bitstream_build_addr = 0xBFD
        self.bitstream_variant_addr = 0xBFE
        self.image_calibration = None
        self.regs_list = [
            Register("ProductID", [0x00], "R"),
            Register("RevisionId", [0x01], "R"),
            Register("Control1", [0x02], "RW"),
            Register("Control2", [0x03], "RW"),
            Register("Status", [0x04], "R"),
            Register("DeltaX", [0x05, 0x06], "R"),
            Register("DeltaY", [0x07, 0x08], "R"),
            Register("SPIConfig", [0x09], "RW"),
            Register("Reset", [0x0A], "RW"),
            Register("ServReq", [0x0B], "RW"),
            Register("ResPgmX", [0x0C], "RW"),
            Register("ResPgmY", [0x0D], "RW"),
            Register("ResPgmStep", [0x0E], "RW"),
            Register("IntegTime", [0x10], "R"),
            Register("LED", [0x11], "R"),
            Register("FlashRate", [0x12, 0x13], "R"),
            Register("SFMax", [0x14], "R"),
            Register("CompSet", [0x15], "R"),
            Register("LiftStat", [0x16], "R"),
            Register("NoEdgeCntX", [0x17], "R"),
            Register("NoEdgeCntY", [0x18], "R"),
            Register("InvEdgeCntX", [0x19], "R"),
            Register("InvEdgeCntY", [0x1A], "R"),
            Register("BalanceXY", [0x1B], "RW"),
            Register("ResCor", [0x1C, 0x1D], "RW"),
            Register("PwrMaxFrate", [0x1F], "RW"),
            Register("Rest1Frate", [0x20], "RW"),
            Register("Rest2Frate", [0x21], "RW"),
            Register("Rest1-2Time", [0x22], "RW"),
            Register("Rest-STime", [0x23], "RW"),
            Register("StrongSlopeThX", [0x24], "RW"),
            Register("WeakSlopeThX", [0x25], "RW"),
            Register("SurfLowerTh", [0x27], "RW"),
            Register("SurfUpperTh", [0x28], "RW"),
            Register("SensorEval", [0x29], "RW"),
            Register("PixVoltageTrim", [0x30], "RW"),
            Register("PixCurTrim", [0x31], "RW"),
            Register("OscTrim1", [0x32], "RW"),
            Register("OscTrim2", [0x33], "RW"),
            Register("OscTrim3", [0x34], "RW"),
            Register("LEDTrim", [0x35], "RW"),
            Register("VDDTrim", [0x36], "RW"),
            Register("LiftLevel", [0x50], "RW"),
            Register("SlpInd", [0x51], "RW"),
            Register("SlpCtrl", [0x52], "RW"),
            Register("SurfClass", [0x53], "R"),
            Register("FixSurfClass", [0x54], "RW"),
            Register("DPICalDeltaX", [0x55, 0x56], "RW"),
            Register("DPICalDeltaY", [0x57, 0x58], "RW"),
            Register("SlpDisp", [0x5B, 0x5C], "RW"),
            Register("SurfRangeTh", [0x5D], "RW"),
            Register("BalanceXY1", [0x5F], "RW"),
            Register("FixIntegTime", [0x60], "RW"),
            Register("FixLED", [0x61], "RW"),
            Register("FixFlashRate", [0x62, 0x63], "RW"),
            Register("FixSFMax", [0x64], "RW"),
            Register("FixCompSet", [0x65], "RW"),
            Register("PixelDump", [0x66], "Rw"),
            Register("PixCol", [0x67], "RW"),
            Register("PixRow", [0x68], "RW"),
            Register("PixelSel", [0x70], "RWU"),
            Register("PixelOut", [0x71, 0x72], "R"),
            Register("EdgeStream1", [0x73], "RW"),
            Register("EdgeStream2", [0x74], "RW"),
            Register("TestPads", [0x75], "RW"),
            Register("TestPassword", [0x76], "RW"),
            Register("TestSelect", [0x77], "RW"),
            Register("TestOscillator", [0x78], "RW"),
            Register("TestMode1", [0x79], "RW"),
            Register("TestMode2", [0x7A], "RW"),
            Register("TestMode3", [0x7B], "RW"),
            Register("ClkReg", [0x7C], "RW"),
            Register("PageSel", [0x7F], "RW"),
        ]
        self.regs = {}
        for reg in self.regs_list:
            self.regs[reg.name] = reg

        self.__post_init__()

    def enable_bitstream_upload(self):
        self.transmission([0x2A, 0xCF, 0x2B, 0x06])
        self.transmission([0x2C, 0x10, 0x2D, 0x00])

    def automated_image_dump(self):
        self.dumped_image = []
        self.fw_stop()
        self.cs_enable()
        self.control1_value = self.read_register("Control1")
        self.write_register("Control1", 0x00)
        self.cs_disable()

        # Flashes
        self.cs_enable()
        #        self.write_register(self.reg["Reset"], 0xB8)
        self.write_register("Control1", 0x88)
        self.cs_disable()
        sleep(0.05)
        self.cs_enable()
        self.write_register("Control1", 0x00)
        #       self.write_register(self.reg["Reset"], 0xB8)
        self.cs_disable()

        # data RAM read procedure
        self.cs_enable()
        self.transmission([0x2A, 0xCF, 0x2B, 0x02, 0x2C, 0x1B, 0x2D, 0x00])

        step = 4  # strictly smaller than 8
        nb_pixels = self.width * self.height
        for i in range(0, nb_pixels, step):
            sdi = self.transmission([0xAE, 0xAF, 0x80] * step)
            self.dumped_image.extend(
                [(sdi[i * 3 + 1] * 256 + sdi[i * 3 + 2]) / 8 for i in range(step)]
            )
            if callable(self.image_dump_progress_callback):
                self.image_dump_progress_callback(i * 100 // nb_pixels)

        self.transmission([0x2A, 0x00])
        self.cs_disable()

        self.end_image_dump()
        return self.dumped_image

    def manual_image_dump(self):
        import time

        tic = time.time()
        self.dumped_image = []
        self.fw_stop()
        self.cs_enable()
        self.control1_value = self.read_register("Control1")
        self.write_register("Control1", 0x00)
        self.cs_disable()
        self.cs_enable()
        for i in range(self.width):
            self.write_register("PixCol", i)
            self.write_register("Control1", 0x05)
            while self.read_register("Control1") & 0x01:
                pass
            self.write_register("PixelSel", 0x00)
            pixels = self.read_registers(["PixelOut"] * 40)  # second loop here
            self.dumped_image.extend(pixels)
            if callable(self.image_dump_progress_callback):
                self.image_dump_progress_callback(i * 100 // self.width)

        self.write_register("Reset", 0xB8)
        self.cs_disable()
        print(time.time() - tic)

        self.end_image_dump()
        return self.dumped_image
