from .sensor import Sensor
from time import sleep
from .register import Register


class Em7795(Sensor):
    def __init__(self, interface):
        Sensor.__init__(self, interface)
        self.name = "Saturn"
        self.dumped_image = None
        self.bistream_start_addr = 0x1000
        self.bitstream_version_addr = 0x03
        self.bitstream_build_addr = 0x04
        self.bitstream_variant_addr = 0x00
        self.width = 40
        self.height = 40
        self.regs_list = [
            Register("ProductID", [0x00]),
            Register("RevisionId", [0x01]),
            Register("Control1", [0x02]),
            Register("Control2", [0x03]),
            Register("Status", [0x04]),
            Register("DeltaX", [0x05, 0x06]),
            Register("DeltaY", [0x07, 0x08]),
            Register("SPIConfig", [0x09]),
            Register("Reset", [0x0A]),
            Register("ServReq", [0x0B]),
            Register("ResPgmX", [0x0C]),
            Register("ResPgmY", [0x0D]),
            Register("ResPgmStep", [0x0E]),
            Register("IntegTime", [0x10]),
            Register("LED", [0x11]),
            Register("FlashRate", [0x12, 0x13]),
            Register("SFMax", [0x14]),
            Register("CompSet", [0x15]),
            Register("LiftStat", [0x16]),
            Register("NoEdgeCntX", [0x17]),
            Register("NoEdgeCntY", [0x18]),
            Register("InvEdgeCntX", [0x19]),
            Register("InvEdgeCntY", [0x1A]),
            Register("SensorEval", [0x29]),
            Register("PixVoltageTrim", [0x30]),
            Register("PixCurTrim", [0x31]),
            Register("OscTrim1", [0x32]),
            Register("OscTrim2", [0x33]),
            Register("OscTrim3", [0x34]),
            Register("LEDTrim", [0x35]),
            Register("Error", [0x4D]),
            Register("QualityAccumulator", [0x4E]),
            Register("FrameStatus", [0x4F]),
            Register("BadFrameCount", [0x5A, 0x59]),
            Register("RecoveredFrameCount", [0x5C, 0x5B]),
            Register("FirmwareVersion", [0x5E, 0x5D]),
            Register("FixIntegTime", [0x60]),
            Register("FixLED", [0x61]),
            Register("FixFlashRate", [0x62, 0x63]),
            Register("FixSFMax", [0x64]),
            Register("FixCompSet", [0x65]),
            Register("PixelDump", [0x66]),
            Register("PixCol", [0x67]),
            Register("PixRow", [0x68]),
            Register("RTE0", [0x69, 0x6C]),
            Register("RTE1", [0x6A, 0x6D]),
            Register("RTE2", [0x6B, 0x6E]),
            Register("RTELocSel", [0x6F]),
            Register("PixelSel", [0x70]),
            Register("PixelOut", [0x71, 0x72]),
            Register("TestPads", [0x75]),
            Register("TestPassword", [0x76]),
            Register("TestSelect", [0x77]),
            Register("TestOscillator", [0x78]),
            Register("TestMode1", [0x79]),
            Register("TestMode2", [0x7A]),
            Register("TestMode3", [0x7B]),
            Register("ClkReg", [0x7C]),
        ]
        self.regs = {}
        for reg in self.regs_list:
            self.regs[reg.name] = reg
        self.__post_init__()

    def enable_bitstream_upload(self):
        self.transmission([0x2A, 0xCF, 0x2B, 0x06])
        self.transmission([0x2C, 0x10, 0x2D, 0x00])

    def read_dpe(self):
        self.cs_enable()
        self.transmission([0x2A, 0xCF])
        dpe = []
        for row in range(self.height):
            dpe_row = []
            for col in range(self.width):
                bits1 = 0x6 << 4 | row >> 2
                bits2 = ((row & 0b11) << 6) | col
                self.transmission(
                    [
                        0x2B,
                        0x05,
                        0x2D,
                        0xB0,
                        0x2E,
                        bits1,
                        0x2F,
                        bits2,
                        0x2B,
                        0x01,
                        0x2D,
                        0xB3,
                    ]
                )
                sdo = self.transmission([0xAE, 0xAF, 0x80])
                dpe_coef = sdo[1] << 8 | sdo[2]
                dpe_row.append(dpe_coef)
                if callable(self.image_dump_progress_callback):
                    self.image_dump_progress_callback(
                        (row * self.height + col) * 100 // (self.height * self.width)
                    )
            dpe.append(dpe_row)
        if callable(self.image_dump_progress_callback):
            self.image_dump_progress_callback(100)

        self.transmission([0x2A, 0x00])
        self.cs_disable()

        return dpe

    def automated_image_dump(self):
        self.dumped_image = []
        self.control1_value = self.read_register("Control1")
        self.fw_stop()
        self.cs_enable()
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
        self.transmission([0x2A, 0xCF, 0x2B, 0x02, 0x2C, 0x14, 0x2D, 0x00])

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
            self.image_dump_progress_callback(i * 100 // self.width)

        self.write_register("Reset", 0xB8)
        self.cs_disable()
        print(time.time() - tic)

        self.end_image_dump()
        return self.dumped_image

    def restart(self):
        self.write_register()
