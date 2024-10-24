""" Classes for types and parameters """

import ctypes


class Type:
    """ A class representing ctypes types. """

    type_str_dict = {"char": ctypes.c_char,
                     "short": ctypes.c_short,
                     "int": ctypes.c_int,
                     "long": ctypes.c_long,
                     "bool": ctypes.c_bool,
                     "size_t": ctypes.c_size_t,
                     "char*": ctypes.c_char_p,
                     "void*": ctypes.c_void_p,
                     "void": None
    }

    def __init__(self, c_str):
        self.c_str = c_str
        if c_str in self.type_str_dict:
            self.c_type = self.type_str_dict[c_str]
        else:
            raise ValueError(f"type_str '{c_str}' not understood")

    def __str__(self):
        return self.c_str


class Parameter:
    """ A class representing parameters to C functions. """

    def __init__(self, param_str):
        type_str, self.name = param_str.rsplit(" ", 1)
        self.type = Type(type_str)

    def __str__(self):
        return f"{self.type} {self.name}"
