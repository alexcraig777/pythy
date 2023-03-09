import types

from .. import interface


def test_basic_functionality():
    """ Tests basic functionality """
    class_lib = interface.create_interface("classes_basic.h", "./classes.so")

    r = class_lib.Rectangle(2, 5)
    print(dir(r))
    assert r.get_area() == 10
    assert r.get_rect_description() == b"This is a 2x5 rectangle!"
    r.clean_up()
