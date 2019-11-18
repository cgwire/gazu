"""
Contains utility routines to be used in gazu tests
"""

import binascii


def fakeid(string):
    """
    Returns a mock uuid from text.

    Result is consistent (same text will yield the same uuid).
    """
    hex_string = binascii.hexlify(string.encode()).decode()
    return "{:0<8}-{:0<4}-{:0<4}-{:0<4}-{:0<12}".format(
        hex_string[0:8],
        hex_string[8:12],
        hex_string[12:16],
        hex_string[16:20],
        hex_string[20:32],
    )
