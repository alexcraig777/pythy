# pythy

A short and sweet Python interface to compiled code


## Overview

`pythy` dynamically generates a Python interface for calling
functions in a shared library using the interface exposed by a
C header file.

`pythy`'s coolest feature is its ability to run compiled code under
the Valgrind debugger. This allows you to test compiled code for
memory errors directly from Python, for example while running
automated testing.


## Installation

`pip install pythy`


## Minimal example

Create `add.c` with the following contents:

```c
#include "add.h"

int add(int a, int b) {
    return a + b;
}
```

and `add.h` with

```c
int add(int a, int b);
```

The compile `add.c` into a Linux shared object with the command
`gcc -fPIC -shared funcs.c -o funcs.so`.

Then run the following Python code, which creates a module `module`
and populates it with a wrapper for the `add` function from your C
code, complete with the correct type information:

```python
import pythy

module = pythy.create_interface("add.h", "add.so")
print(module.add(1, 2))
```

That's it! You've run your compiled C code directly from Python.

`pythy` also has the ability to generate docstrings from your header
file and even automatically create classes.


## Minimal example with Valgrind

TODO: Add a minimal example demonstrating usage with Valgrind.


## Memory spaces

TODO: Move this section to a C implementation guide.

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
