import pytest
import types

import pythy


modes = ["ctypes", "sockapi"]

def test_get_started():
    """ Test the "Get Started" example from the docs """
    adder = pythy.create_interface("add.h", "add.so")
    assert adder.add(1, 2) == 3

@pytest.mark.parametrize("mode", modes)
def test_basic_functionality(mode):
    """ Tests basic functionality """
    pythy.backend.set_mode(mode)

    func_lib = pythy.create_interface("funcs_basic.h", "funcs.so")

    assert func_lib.add(1, 2) == 3
    assert func_lib.get_len(b"hello") == 5
    new_str = func_lib.concatenate(b"hel", b"lo!")
    assert new_str == b"hello!"

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_bind_to_prior_module(mode):
    """ Tests ability to bind to a prior module, rather than create one
    and bind to it internally """
    pythy.backend.set_mode(mode)

    func_lib = types.ModuleType("func_lib")
    new_func_lib = pythy.create_interface("funcs_basic.h", "funcs.so",
                                          module = func_lib)
    assert new_func_lib is func_lib

    assert func_lib.add(1, 2) == 3
    assert func_lib.get_len(b"hello") == 5
    new_str = func_lib.concatenate(b"hel", b"lo!")
    assert new_str == b"hello!"

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_docs(mode):
    """ Tests the function doc-string generation """
    pythy.backend.set_mode(mode)

    func_lib = pythy.create_interface("funcs_basic.h", "funcs.so")

    # The name should be the basename of the library file up until
    # the last period.
    assert func_lib.__name__ == "funcs"

    assert func_lib.add.__doc__ == "Adds 2 integers"
    assert func_lib.get_len.__doc__ == "Finds the length of a string"
    assert func_lib.concatenate.__doc__ == "Concatenates 2 strings"

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_alias(mode):
    """ Tests function aliasing """
    pythy.backend.set_mode(mode)

    func_lib = pythy.create_interface("funcs_alias.h", "funcs.so")
    assert func_lib.cat(b"hel", b"lo!") == b"hello!"

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_built_in_wrappers(mode):
    """ Tests the built-in wrappers

    In the header file we specify that all string arguments should be
    encoded, and all string returns decoded. """

    pythy.backend.set_mode(mode)

    func_lib = pythy.create_interface("funcs_built_in_wrappers.h",
                                      "funcs.so")
    assert func_lib.get_len("hello") == 5
    assert func_lib.concatenate("hel", "lo!") == "hello!"

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_custom_wrappers(mode):
    """ Tests custom wrappers

    In the header file we specifiy:
    - the arguments to `add` should be incremented
    - the return value from `get_len` should be doubled """

    pythy.backend.set_mode(mode)

    import custom_wrappers
    func_lib = pythy.create_interface("funcs_custom_wrappers.h",
                                      "funcs.so",
                                      wrapper_modules = [custom_wrappers])
    assert func_lib.add(3, 5) == 10
    assert func_lib.get_len(b"hello!") == 12

    func_lib.close()

@pytest.mark.parametrize("mode", modes)
def test_func_regex(mode):
    """ Tests simple regex matching for function wrapping

    In the header we specify that the `increment_args` applies only
    to `add` (by saying it applies to everything, then excluding the
    others), and that `double_rtn` applies to everything except
    `add`. """
    pythy.backend.set_mode(mode)

    import custom_wrappers
    func_lib = pythy.create_interface("funcs_simple_regex.h",
                                      "funcs.so",
                                      wrapper_modules = [custom_wrappers])

    assert func_lib.add(17, 42) == 61
    assert func_lib.get_len(b"hello!") == 12
    assert func_lib.concatenate(b"hel", b"lo!") == b"hello!hello!"

    func_lib.close()
