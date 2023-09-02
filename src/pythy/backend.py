""" Generic interface for calling compiled code from Python

This can operate in 2 modes:
1. ctypes mode, which uses ctypes to call into a .so with the
   compiled code running in the same process as the Python code.

2. sockapi mode, which uses `sockapi.py` to make function calls
   over a socket to compiled code running in a different process.
"""

import ctypes
import os

from . import sockapi


default_mode = "ctypes"


def set_mode(mode):
    """ Set the module of operation

    Options for `mode`:
    - ctypes: Run the compiled code in the same process, mediated by
              the `ctypes` package.
    - sockapi: Run the compiled code in a different process with
               function calls made by the custom `sockapi` module.
    """
    global default_mode
    if mode not in Backend._modes:
        raise ValueError(f"Unsupported backend mode: {mode}")
    default_mode = mode


class Backend:
    _modes = {"ctypes", "sockapi"}

    def __init__(self, library_file, mode = None):
        if not (library_file.startswith("/") or
                library_file.startswith(".")):
            library_file = os.path.join(".", library_file)
        self.library_file = library_file
        if mode is None:
            self.mode = default_mode
        elif mode not in self._modes:
            raise ValueError("mode '{mode}' not allowed")
            self.mode = mode

    def open_library(self):
        """ Initialize the shared object """
        if self.mode == "ctypes":
            self.lib = ctypes.cdll.LoadLibrary(self.library_file)
        else:
            self.lib = sockapi.Session(self.library_file)

    def get_function(self, func, arg_types, rtn_type):
        """ Create a Python function to call into the shared object """
        if self.mode == "ctypes":
            func = getattr(self.lib, func)
            func.argtypes = arg_types
            func.restype = rtn_type
        else:
            func = self.lib.make_function(func, arg_types, rtn_type)
        return func

    def close(self):
        """ Close the shared object

        What actually happens depends on what mode the backend was
        created in:
        - ctypes: If the library has a destructor function, it's called.
          There doesn't seem to be a way to forcibly unload the library
          itself from memory.
        - sockapi: We send the `exit` API message to the server. This
          will take care of unloading the library entirely.

        Returns True if the library was successfully closed; False
        if the library doesn't provide a destructor function.
        Raises `ValueError` in sockapi debug mode if there were
        Valgrind errors. """
        rtn = False

        if self.mode == "ctypes":
            if hasattr(self.lib, "destructor"):
                self.lib.destructor.argtypes = []
                self.lib.destructor.restype = None
                self.lib.destructor()
                rtn = True

        else:
            self.lib.stop_server()
            rtn = True

            with open("vg-log.txt", "r") as f:
                vg_log = f.read()

            if "0 errors from 0 contexts" not in vg_log:
                print("==========================")
                print(vg_log)
                print("==========================")
                raise ValueError("Valgrind found errors!")
            else:
                print("Valgrind reported no errors!")

        return rtn
