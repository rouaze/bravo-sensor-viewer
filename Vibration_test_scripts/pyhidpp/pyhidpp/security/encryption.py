import base64
from Crypto.Cipher import AES
import configparser

from ..core.logger import get_pyhidpp_logger
import pathlib


class AESCipher(object):
    def __init__(self, tdeOffuscatedFileName: str):
        self.logger = get_pyhidpp_logger()
        config = configparser.ConfigParser()
        config.read(pathlib.Path(__file__).parent / "x1602.ini")
        self.bs = AES.block_size
        # self.key = hashlib.sha256(key.encode()).digest()
        self.key = bytes(eval(config["AES"]["key"]))
        self.iv = bytes(eval(config["AES"]["iv"]))
        self.passwords = configparser.ConfigParser()
        self.passwords.read(tdeOffuscatedFileName)

    def decrypt(self, fw, session_name):
        password = self.passwords[fw][session_name]
        enc = base64.b64decode(password)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decipher = cipher.decrypt(enc)
        decipher_unpad = decipher[4:-12]
        decipher_bytes = []
        for i in range(0, len(decipher_unpad), 2):
            decipher_bytes.append(int(decipher_unpad[i : i + 2], 16))
        return decipher_bytes

    def encrypt(self, data: list[int]):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data_padded = (
            b" \x00\x00\x00"
            + bytes("".join(["{:02X}".format(x) for x in data]), "utf-8")
            + b"\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        enc = cipher.encrypt(data_padded)
        return base64.b64encode(enc).decode("utf-8")
