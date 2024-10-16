pythy: a clean Python interface to compiled code
================================================

.. toctree::
    :caption: Contents:
    :hidden:

    get-started
    main
    issues

Welcome to ``pythy``! Thanks for coming.

**pythy allows you to easily run compiled code from Python.**

It also allows you to use Valgrind to debug your compiled code while
running it from Python!

Comparison with ``ctypes``
--------------------------

*TLDR: pythy allows you to use a C header file to specify the interface
with a shared object, instead of having to specify prototypes in your
Python code.*

The best way to understand ``pythy`` is to compare it with ``ctypes``
(the builtin Python foreign-function library, which ``pythy`` uses by
default under the hood).

To run compiled code with ``ctypes`` you must:

#. Load a shared object.
#. Create a Python function wrapper by explicitly specifying the
   function name and prototype *in your Python code*.
#. Call the Python wrapper.

Using ``pythy``, you must:

#. Provide a shared object.
#. Provide *a C header file* describing the function(s) and prototype(s).
#. Call the Python wrapper.

The key difference is that instead of specifying the functions and
prototypes `in Python code`, you specify them `in a C header file`.
This should be much more intuitive and maintainable for C developers,
primarily because *a shared object file will probably already have a
header file associated with it*.

Valgrind debugging
------------------

Unlike ``ctypes``, ``pythy`` also allows you to use Valgrind to debug
your compiled code while running it from Python. This is pretty much
impossible using ``ctypes`` because it loads the shared object *into
the same memory space as the Python interpreter itself*. Thus, Valgrind
must run on the Python process itself, which is problematic because
Valgrind finds and reports many errors from the Python interpreter,
masking errors and warnings produced by your code. ``pythy``, on the
other hand, includes an option to run the compiled code under Valgrind
*in an entirely different process* so that errors from your code can
be reported accurately.
