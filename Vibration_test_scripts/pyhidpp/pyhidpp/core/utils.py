"""
HIDPP utils
utility functions

suffix _le = little endian
suffix _be = big endian
"""

import logging
import struct

UNIFYING_RECEIVER_PID = [
    0xC526,
    0xC527,
    0xC528,
    0xC529,
    0xC52A,
    0xC52B,
    0xC52C,
    0xC52D,
    0xC52E,
    0xC52F,
    0xC530,
    0xC531,
    0xC532,
    0xC533,
    0xC534,
    0xC535,
    0xC536,
    0xC537,
    0xC538,
    0xC539,
    0xC53A,
    0xC53B,
    0xC53C,
    0xC53D,
    0xC53E,
    0xC53F,
    0xC540,
    0xC541,
    0xC542,
    0xC543,
    0xC544,
    0xC545,
    0xC546,
    0xC547,
    0xC549,
    0xC54A,
    0xC54D,
    0xC54E,
]
BLE_PRO_RECEIVER_PID = [
    0xC548,
    0xC54B,
    0xC54C,
]

BOLT_DEVICE_TYPE = {
    0x00: "Unknown",
    0x01: "Keyboard",
    0x02: "Mouse",
    0x03: "Numpad",
    0x04: "Presenter",
    0x07: "Remote control",
    0x08: "Trackball",
    0x09: "Touch-pad (relative displacement)",
    0x0A: "Tablet / Touchpad (absolute coordinates)",
    0x0B: "Gamepad",
    0x0C: "Joystick",
    0x0D: "Dial",
}

DEVICE_TYPE = {
    0: "Keyboard",
    1: "Remote Control",
    2: "Numpad",
    3: "Mouse",
    4: "Trackpad",
    5: "Trackball",
    6: "Presenter",
    7: "Receiver",
    8: "Headset",
    9: "Webcam",
    10: "Steering Wheel",
    11: "Joystick",
    12: "Gamepad",
    13: "Dock",
    14: "Speaker",
    15: "Microphone",
    16: "Light",
    17: "Programmable controller",
    18: "Car Sim Pedals",
}


logger = logging.getLogger("hidpp")

def list_to_hex_string(input_list):
    hex_list = [hex(num)[2:].upper().zfill(2) for num in input_list]
    hex_string = ' '.join(hex_list)
    return hex_string

def u16_to_list_le(val):
    return list(struct.pack("<H", val))


def u16_to_list_be(val):
    return list(struct.pack(">H", val))


def i16_to_list_le(val):
    return list(struct.pack("<h", val))


def i16_to_list_be(val):
    return list(struct.pack(">h", val))


def u32_to_list_le(val):
    return list(struct.pack("<I", val))


def u32_to_list_be(val):
    return list(struct.pack(">I", val))


def i32_to_list_le(val):
    return list(struct.pack("<i", val))


def i32_to_list_be(val):
    return list(struct.pack(">i", val))


def float_to_list_le(val):
    return list(struct.pack("<f", val))


def float_to_list_be(val):
    return list(struct.pack(">f", val))


def list_to_u16_le(array):
    if len(array) != 2:
        logger.error("Wrong array size")
        return 0
    return struct.unpack("<H", bytearray(array))[0]


def list_to_u16_be(array):
    if len(array) != 2:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">H", bytearray(array))[0]


def list_to_i16_le(array):
    if len(array) != 2:
        logger.error("Wrong array size")
        return 0
    return struct.unpack("<h", bytearray(array))[0]


def list_to_i16_be(array):
    if len(array) != 2:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">h", bytearray(array))[0]


def list_to_u32_le(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack("<I", bytearray(array))[0]


def list_to_u32_be(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">I", bytearray(array))[0]


def list_to_i32_le(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack("<i", bytearray(array))[0]


def list_to_i32_be(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">i", bytearray(array))[0]


def list_to_float_le(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack("<f", bytearray(array))[0]


def list_to_float_be(array):
    if len(array) != 4:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">f", bytearray(array))[0]


def list_to_i8(array):
    if len(array) != 1:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">b", bytearray(array))[0]


def list_to_u8(array):
    if len(array) != 1:
        logger.error("Wrong array size")
        return 0
    return struct.unpack(">B", bytearray(array))[0]


def printConsoleProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def test_utils():
    print("TEST LITTLE ENDIANNESS")
    test_val = 123.456
    res = float_to_list_le(test_val)
    out = list_to_float_le(res)
    print(
        "float test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = 0x0123
    res = u16_to_list_le(test_val)
    out = list_to_u16_le(res)
    print(
        "u16 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = -4321
    res = i16_to_list_le(test_val)
    out = list_to_i16_le(res)
    print(
        "i16 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = 0x01234567
    res = u32_to_list_le(test_val)
    out = list_to_u32_le(res)
    print(
        "u32 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = -7654321
    res = i32_to_list_le(test_val)
    out = list_to_i32_le(res)
    print(
        "i32 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    print("TEST BIG ENDIANNESS")
    test_val = 123.456
    res = float_to_list_be(test_val)
    out = list_to_float_be(res)
    print(
        "float test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = 0x0123
    res = u16_to_list_be(test_val)
    out = list_to_u16_be(res)
    print(
        "u16 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = -4321
    res = i16_to_list_be(test_val)
    out = list_to_i16_be(res)
    print(
        "i16 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = 0x01234567
    res = u32_to_list_be(test_val)
    out = list_to_u32_be(res)
    print(
        "u32 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )

    test_val = -7654321
    res = i32_to_list_be(test_val)
    out = list_to_i32_be(res)
    print(
        "i32 test val: {}, arr: {}, out: {}, error={}".format(
            test_val, res, out, test_val - out
        )
    )


if __name__ == "__main__":
    test_utils()
