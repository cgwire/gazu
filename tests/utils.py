"""
Contains utility routines to be used in gazu tests
"""

import binascii
import json
import gazu.client
import io
import cgi
import sys


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


def add_verify_file_callback(mock, dict_assert={}, url=None):
    def verify_file_callback(request):
        if url is None or url == request.url:
            body_file = io.BytesIO(request.body)
            _, pdict = cgi.parse_header(request.headers["Content-Type"])
            if sys.version_info[0] == 3:
                pdict["boundary"] = bytes(pdict["boundary"], "UTF-8")
            else:
                pdict["boundary"] = bytes(pdict["boundary"])
            parsed = cgi.parse_multipart(fp=body_file, pdict=pdict)
            for key in dict_assert.keys():
                assert key in parsed.keys()
                if isinstance(parsed[key][0], bytes):
                    try:
                        parsed[key][0] = parsed[key][0].decode("utf-8")
                    except UnicodeDecodeError:
                        pass
                assert dict_assert[key] == parsed[key][0]
        return None

    mock.add_matcher(verify_file_callback)
