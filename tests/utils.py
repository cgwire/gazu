"""
Contains utility routines to be used in gazu tests
"""

import binascii
import json
import gazu.client


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


def mock_route(mock, request_type, path="", **kwargs):
    if "text" in kwargs and isinstance(kwargs["text"], (list, dict)):
        kwargs["text"] = json.dumps(kwargs["text"])
    if not (path.startswith("http://") or path.startswith("https://")):
        path = gazu.client.get_full_url(path)
    getattr(mock, request_type.lower())(path, **kwargs)
