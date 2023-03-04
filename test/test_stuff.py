import types

from .. import interface


# Initialize the empty module that we'll fill out.


def test_basic_functionality():
    """ Tests basic functionality """
    stuff = types.ModuleType("stuff")
    interface.create_interface("stuff_basic.h", "./stuff.so", stuff)

    assert stuff.add(1, 2) == 3
    assert stuff.get_len(b"hello") == 5
    new_str = stuff.concatenate(b"hel", b"lo!")
    assert new_str == b"hello!"

def test_docs():
    """ Tests the function doc string generation """
    stuff = interface.create_interface("stuff_basic.h", "./stuff.so")

    # The name should be the basename of the header file up until
    # the last period.
    assert stuff.__name__ == "stuff_basic"

    assert stuff.add.__doc__ == "Adds 2 integers"
    assert stuff.get_len.__doc__ == "Finds the length of a string"
    assert stuff.concatenate.__doc__ == "Concatenates 2 strings"

def test_alias():
    """ Tests function aliasing """
    stuff = interface.create_interface("stuff_alias.h",
                                       "./stuff.so")
    assert stuff.cat(b"hel", b"lo!") == b"hello!"

def test_built_in_wrappers():
    """ Tests the built-in wrapper application

    In the header file we specify that all string arguments should be
    encoded, and all string returns decoded. """

    stuff = interface.create_interface("stuff_built_in_wrappers.h",
                                       "./stuff.so")
    assert stuff.get_len("hello") == 5
    assert stuff.concatenate("hel", "lo!") == "hello!"

def test_custom_wrappers():
    """ Tests application of built-in wrappers

    In the header file we specifiy:
    - the arguments to `add` should be incremented
    - the return value from `get_len` should be doubled """

    from . import custom_wrappers
    stuff = interface.create_interface("stuff_custom_wrappers.h",
                                       "./stuff.so",
                                       wrapper_modules = [custom_wrappers])
    assert stuff.add(3, 5) == 10
    assert stuff.get_len(b"hello!") == 12

def test_func_regex():
    """ Tests simple regex matching for function wrapping

    In the header we specify that the `increment_args` applies only
    to `add` (by saying it applies to everything, then excluding the
    others), and that `double_rtn` applies to everything except
    `add`. """
    from . import custom_wrappers
    stuff = interface.create_interface("stuff_simple_regex.h",
                                       "./stuff.so",
                                       wrapper_modules = [custom_wrappers])

    assert stuff.add(17, 42) == 61
    assert stuff.get_len(b"hello!") == 12
    assert stuff.concatenate(b"hel", b"lo!") == b"hello!hello!"
