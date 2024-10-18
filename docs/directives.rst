:tocdepth: 1

Directive Reference
===================

#. ``define <old-str> -> <new-str>``

   * This performs text replacement.
   * This is the only directive where the arguments can contain spaces.

#. ``class <c-arg-name> [py-name]``

   * This indicates that there's a Python class that will absorb
     some of the interface functions as methods.
   * Specifically, any C function whose first argument is named
     ``c-arg-name`` will automatically become a method of the
     associated Python class.
   * If ``py-name`` is ommitted, Python will choose a nicely formatted
     one based on ``c-arg-name``.

#. ``init <cls-name> <func>``

   * This indicates that a function should be used as the
     ``__init__`` method for a class
   * At one point I thought we could do this purely by aliasing the
     function to ``__init__``, but it's first parameter doesn't have the
     right name, so it wouldn't work.

#. ``func_alias <c-name> <py-name>``

   * This specifies an alternate Python name for a function

#. TODO: byte-array length specification

#. TODO: specify property
