import pytest
import types


import pythy

modes = ["ctypes", "sockapi"]


@pytest.mark.parametrize("mode", modes)
def test_basic_functionality(mode):
    """ Tests basic functionality """
    pythy.backend.default_mode = mode

    class_lib = pythy.create_interface("classes_basic.h", "./classes.so")

    r = class_lib.Rectangle(2, 5)
    assert r.get_area() == 10
    assert r.get_rect_description() == b"This is a 2x5 rectangle!"
    r.clean_up_rectangle()

    b = class_lib.Box(3, 4, 6)
    assert b.get_volume() == 72
    assert b.get_box_description() == b"This is a 3x4x6 box!"
    b.clean_up_box()

    class_lib.close()
