import types

from .. import interface

interface.backend.default_mode = "sockapi"

def test_basic_functionality():
    """ Tests basic functionality """
    class_lib = interface.create_interface("classes_basic.h", "./classes.so")

    r = class_lib.Rectangle(2, 5)
    assert r.get_area() == 10
    assert r.get_rect_description() == b"This is a 2x5 rectangle!"
    r.clean_up_rectangle()

    b = class_lib.Box(3, 4, 6)
    assert b.get_volume() == 72
    assert b.get_box_description() == b"This is a 3x4x6 box!"
    b.clean_up_box()

    class_lib.close()
