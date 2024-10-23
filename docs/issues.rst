:tocdepth: 1

Known Issues
============

I'm running into these issues as I try to use ``pythy`` to interface
with my debugger.

* You should be able to use multiple distinct header files. A single
  shared object will probably have its interface split across multiple
  headers.

* You shouldn't have to use a prefix like ``interface_`` in front of
  all your function names. This defeats the whole purpose of ``pythy``
  because it encourages writing thin C wrappers instead of using
  what's already there.

  I think the original purpose of the prefix was to allow some functions
  in the header file not to be wrapped. We can add a directive for this
  kind of private function.

* There should be a clean way to handle byte arrays that contain
  the zero byte. By default, ``ctypes`` assumes byte arrays are
  null-terminated, but if you're, e.g., reading memory, you
  probably want to be able to return a byte array containg a zero byte
  from C to Python.

  Maybe there can be a new directive that gives the length in bytes
  of an array as an expression of other function parameters.

* Currently a lot of my interface functions return strings that it
  expects Python to parse (for example, to return info on stack frames,
  the current process status, and the current register values). That's
  not very standard for a C API, which would probably return a struct
  and either

  1. expose its definition so that the caller could manually inspect
     the members or
  2. expose thin wrappers that inspect the members and return their
     values.

  Option 1 would require interpreting struct definitions and then
  using ``ctypes`` to inspect memory, which I've avoided so far.
  Option 2 would require lots of extra C code and calls from Python
  to C, which would probably hurt performance.

  We should probably implement option 1 at some point, but until that
  option 2 doesn't require any changes to ``pythy``, but it's more work
  from the C side.

* To make the result from option 2 more Pythonic, ``pythy`` should
  be able to create Python properties when there are methods ``get_x``
  and ``set_x``.

* How do we handle freeing buffers? A few thoughts:

  * There should be some way for the header file to indicate that the
    user is responsible for freeing a buffer when they're done with it.
  * The shared object shouldn't have to expose the standard ``free``
    function, but it must expose custom cleanup functions.
  * Maybe there should be a directive like
    ``$ cleanup <arg-name> <cleanup-func>`` that tells ``pythy`` what
    function should be called to cleanup the parameter?

* I think wrappers were honestly a terrible idea. They should probably
  be applied in Python code after the interface is created.

* It would be great to be able to handle static inline functions exposed
  in the header files. Although, such a function wouldn't actually be
  compiled into the shared object itself, so I don't know how we could.

* We should consider using reStructuredText directives to express
  ``pythy`` directives in C header files.

* We should look into using the ``ctypes`` ``_as_parameter_`` attribute
  in wrapper classes.

* We should be able to load ``libc`` in ``ctypes`` by running
  ``libc = ctypes.util.find_library("c")``. This can be used to access
  the standard ``free`` function without requiring the shared object
  itself to expose it. I don't know how the ``sockapi`` backend could
  handle this.

* We should be able to handle C block comments.

* We should consider using ``pycparser`` to parse the header files for
  us. There are just a few issues with this:

  #. ``pycparser`` takes in preprocessed code, which is a bit of a pain.

  #. ``pycparser`` can't handle comments (since they're removed by the
     preprocessor), and since ``pythy`` needs to handle them, we'd
     have to do at least some parsing manually.

  #. The simplest solution I can think of is to parse the code manually
     for comments and picking out function prototypes, then pass the
     prototypes to ``pycparser`` for parsing. But, honestly, finding
     the prototypes in the first place is the hardest part. And,
     without using any preprocessor, I don't think ``pycparser`` would
     be much more robust than I could do by hand.

  Here's an example of the usage, since it's a bit intense:

  .. code-block:: python

      import pycparser

      proto = "char* stuff(int a, struct thing* x);"
      # Type FileAST
      ast = pycparser.CParser().parse(proto)
      # Type Decl
      decl = ast.ext[0]
      print("Return type:", decl.type.type)
      for param in decl.type.args.params:
          print(param.name, param.type)

Solutions
---------

#. Modify the debugger to use ``pythy`` *(done)*.

#. Modify the debugger C code to integrate with next step.

#. Modify ``pythy`` to:

   * allow multiple header files
   * remove the ``interface_`` prefix
   * be able to ignore some functions
