:tocdepth: 1

Known Issues
============

I'm running into these issues as I try to use ``pythy`` to interface
with my debugger.

* You should be able to use multiple distinct header files. A single
  shared object will probably have the interface split across multiple
  headers.

* You shouldn't have to use a prefix like ``interface_`` in front of
  all your function names. This defeats the whole purpose of ``pythy``
  because it encourages writing thin C wrappers instead of using
  what's already there.

* There should be a clean way to handle byte arrays that contain
  the zero byte. By default, ``ctypes`` assumes byte arrays are
  null-terminated, but if you're, e.g., reading memory, you
  probably want to be able to return a byte array containg a zero byte
  from C to Python.

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

* How do we handle freeing buffers? The interface probably shouldn't
  have to worry about this.
