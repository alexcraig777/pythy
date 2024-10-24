import ctypes

import pytest

import pythy.sockapi


@pytest.mark.parametrize("debug_mode", [False, True])
def test_sockapi(debug_mode):
    s = pythy.sockapi.Session("./funcs.so", "localhost",
        debug=debug_mode)

    add = s.make_function("add", [ctypes.c_int, ctypes.c_int],
        ctypes.c_int)
    assert add(4, 5) == 9

    cat = s.make_function("concatenate",
        [ctypes.c_char_p, ctypes.c_char_p], ctypes.c_char_p)

    assert cat(b"Hello,", b" world!") == b"Hello, world!"

    s.stop_server()
