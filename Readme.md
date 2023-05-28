# Wrap SO

## Overview

`wrapso` dynamically generates a Python interface for calling functions in a
shared library using the interface exposed by a C header file.


## Memory spaces

Strings (i.e., all variables with C type `char*`) are passed between Python
and the compiled code by passing the literal bytes in the string (without
the null terminator). All other data types are passed as a numerical value.

To take care of allocated memory, when compiled code returns a `char*`

1. The Python code is not responsible for any direct cleanup, except
   for calling `dlclose` on the SO.

2. The returned pointer is guaranteed to remain valid until another function
   in the same SO is called.

This is most easily implemented by the SO maintaining a global `char*`
variable that tracks the last `char*` returned from a function. Whenever
another `char*` must be allocated and returned, the global is realloced
and returned.

This doesn't scale well to multi-threaded programs, but for now it seems
like the easiest way to do things.
