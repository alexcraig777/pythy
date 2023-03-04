def double_rtn(interface_function):
    """ Doubles the return value """
    orig_py_func = interface_function.py_func

    def wrap(*args):
        return 2 * orig_py_func(*args)

    interface_function.py_func = wrap

def increment_args(interface_function):
    """ Increments all the arguments """
    orig_py_func = interface_function.py_func

    def wrap(*args):
        new_args = [arg + 1 for arg in args]
        return orig_py_func(*new_args)

    interface_function.py_func = wrap

