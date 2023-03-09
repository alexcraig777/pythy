import types

from .. import interface


def test_basic_functionality():
    """ Tests basic functionality """
    func_lib = interface.create_interface("funcs_basic.h", "./funcs.so")

    assert func_lib.add(1, 2) == 3
    assert func_lib.get_len(b"hello") == 5
    new_str = func_lib.concatenate(b"hel", b"lo!")
    assert new_str == b"hello!"

def test_bind_to_prior_module():
    """ Tests ability to bind to a prior module, rather than create one
    and bind to it internally """
    func_lib = types.ModuleType("func_lib")
    new_func_lib = interface.create_interface("funcs_basic.h",
                                               "./funcs.so",
                                               module = func_lib)
    assert new_func_lib is func_lib

    assert func_lib.add(1, 2) == 3
    assert func_lib.get_len(b"hello") == 5
    new_str = func_lib.concatenate(b"hel", b"lo!")
    assert new_str == b"hello!"

def test_docs():
    """ Tests the function doc string generation """
    func_lib = interface.create_interface("funcs_basic.h", "./funcs.so")

    # The name should be the basename of the header file up until
    # the last period.
    assert func_lib.__name__ == "funcs_basic"

    assert func_lib.add.__doc__ == "Adds 2 integers"
    assert func_lib.get_len.__doc__ == "Finds the length of a string"
    assert func_lib.concatenate.__doc__ == "Concatenates 2 strings"

def test_alias():
    """ Tests function aliasing """
    func_lib = interface.create_interface("funcs_alias.h",
                                       "./funcs.so")
    assert func_lib.cat(b"hel", b"lo!") == b"hello!"

def test_built_in_wrappers():
    """ Tests the built-in wrapper application

    In the header file we specify that all string arguments should be
    encoded, and all string returns decoded. """

    func_lib = interface.create_interface("funcs_built_in_wrappers.h",
                                       "./funcs.so")
    assert func_lib.get_len("hello") == 5
    assert func_lib.concatenate("hel", "lo!") == "hello!"

def test_custom_wrappers():
    """ Tests application of built-in wrappers

    In the header file we specifiy:
    - the arguments to `add` should be incremented
    - the return value from `get_len` should be doubled """

    from . import custom_wrappers
    func_lib = interface.create_interface("funcs_custom_wrappers.h",
                                       "./funcs.so",
                                       wrapper_modules = [custom_wrappers])
    assert func_lib.add(3, 5) == 10
    assert func_lib.get_len(b"hello!") == 12

def test_func_regex():
    """ Tests simple regex matching for function wrapping

    In the header we specify that the `increment_args` applies only
    to `add` (by saying it applies to everything, then excluding the
    others), and that `double_rtn` applies to everything except
    `add`. """
    from . import custom_wrappers
    func_lib = interface.create_interface("funcs_simple_regex.h",
                                       "./funcs.so",
                                       wrapper_modules = [custom_wrappers])

    assert func_lib.add(17, 42) == 61
    assert func_lib.get_len(b"hello!") == 12
    assert func_lib.concatenate(b"hel", b"lo!") == b"hello!hello!"
