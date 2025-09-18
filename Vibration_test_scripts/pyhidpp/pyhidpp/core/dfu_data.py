import logging

class DfuData:
    """
    used to store dfu data
    """

    def __init__(self):
        self.logger = logging.getLogger("hidpp")
        self.reset()

    def reset(self):
        self.filename = ""
        self.ready_for_update = False
        self.file_loaded = False

        self.file_content = None

        self.tot_line = 0
        self.seqNb = 0

        self.entityIdx = 0
        self.encrypt = 0
        self.magicStr = ""
        self.flag = 0
        self.securLvl = 0

        self.dfu_ongoing = False

    def set_dfu_file(self, filename):
        # first reset (if a previous file was loaded)
        self.reset()

        try:
            dfu_file = open(filename, "rb")
        except OSError:
            self.logger.error("Cannot open dfu file")
            self.file_loaded = False
            return False
        else:
            self.filename = filename
            self.file_content = dfu_file.read()
            dfu_file.close()

        # how to chek if file is correct ?
        # (not really possible as any files can be opened as binary)

        self.tot_line = int(len(self.file_content) / 16)

        self.file_loaded = True
        self.seqNb = 0
        self.extract_info()

        return True

    def extract_line(self, line_nb):
        # extract line data
        line_data = list(self.file_content[line_nb * 16 : (line_nb + 1) * 16])
        return line_data

    def extract_info(self):
        first_line_data = self.extract_line(0)

        self.entityIdx = first_line_data[0]
        self.encrypt = first_line_data[1]
        self.magicStr = ""
        for i in range(10):
            c = first_line_data[2 + i]
            if c == 0:
                break
            else:
                self.magicStr += chr(c)

        self.flag = first_line_data[12]
        self.securLvl = first_line_data[13]

        self.ready_for_update = True

    def print_dfu_info(self):
        self.logger.info("DFU info:")
        self.logger.info("Entity: {}".format(self.entityIdx))
        self.logger.info("magicStr: {}".format(self.magicStr))
        self.logger.info("flag: {}".format(self.flag))
        self.logger.info("securLvl: {}".format(self.securLvl))
        self.logger.info("Size: {} bytes".format(self.tot_line * 16))

    def inc_seqNb(self):
        self.seqNb += 1
        if self.seqNb >= 4:
            self.seqNb = 0

    def get_seqNb(self):
        return self.seqNb

    def get_dfu_info_list(self):
        return (self.entityIdx, self.magicStr, self.flag, self.securLvl, self.tot_line)