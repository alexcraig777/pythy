""" Built-in wrappers for interface functions """

from . import variable


def init_method(interface_function):
    """ The wrapper for InterfaceFunctions that represent
    the __init__ method of a class. """

    # We need to save off the original `py_func` out here so that we
    # don't get into infinite recursion when the wrapper is called.
    orig_py_func = interface_function.py_func

    interface_function.py_params.insert(0, variable.Parameter("void* self"))

    def wrap(self, *args):
        self.ptr = orig_py_func(*args)

    interface_function.py_func = wrap

def generic_method(interface_function):
    """ The wrapper for InterfaceFunctions that represent
    generic methods of a class. """

    orig_py_func = interface_function.py_func

    interface_function.py_params[0].name = "self"

    def wrap(self, *args):
        return orig_py_func(self.ptr, *args)

    interface_function.py_func = wrap

def encode_string_args(interface_function):
    """ The wrapper that encodes all string arguments into bytes. """

    orig_py_func = interface_function.py_func

    def wrap(*args):
        # I considered using the types of the interface_function.py_params
        # to decide whether or not to encode them, but this will allow
        # type errors to propagate more directly into ctypes to be caught
        # there.
        new_args = [arg.encode("utf-8") + b"\x00" if isinstance(arg, str) else arg
                    for arg in args]
        return orig_py_func(*new_args)

    interface_function.py_func = wrap

def decode_string_rtn(interface_function):
    """ The wrapper that decodes string return values. """

    orig_py_func = interface_function.py_func

    def wrap(*args):
        rtn = orig_py_func(*args)
        if isinstance(rtn, bytes):
            rtn = rtn.decode("utf-8")
        return rtn

    interface_function.py_func = wrap
