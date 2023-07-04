""" Classes for types and parameters """

import ctypes

from . import split


class Type:
    """ A class representing ctypes types. """

    type_str_dict = {ctypes.c_char: "char",
                     ctypes.c_short: "short",
                     ctypes.c_int: "int",
                     ctypes.c_long: "long",
                     ctypes.c_bool: "bool",
                     ctypes.c_size_t: "size_t",
                     ctypes.c_char_p: "char*",
                     ctypes.c_void_p: "void*",
                     None: "void"}

    def __init__(self, c_str):
        self.c_str = c_str
        for ct, t_str in self.type_str_dict.items():
            if t_str == c_str:
                self.c_type = ct
                break
        else:
            raise ValueError("type_str '{}' not understood".format(c_str))

    def __str__(self):
        return self.c_str


class Parameter:
    """ A class representing parameters to C functions. """

    def __init__(self, param_str):
        type_str, self.name = split.split_at_last_space(param_str)
        self.type = Type(type_str)

    def __str__(self):
        return "{} {}".format(self.type, self.name)
