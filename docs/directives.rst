:tocdepth: 1

Directive Reference
===================

#. ``define <old-str> -> <new-str>``

   * This tells ``pythy`` to perform text replacement on the file
     contents before parsing it.
   * Each ``define`` directive only affects text *following it in the
     same file*.
   * This is the only directive whose arguments can contain spaces.
   * We might really be able to do without this. Our current use cases
     are:

     * Changing unusual pointer types to ``void*``.
     * Getting rid of the ``const`` qualifier

     Both of these we could hard-code in. For now we should just leave
     it.

#. ``class <c-arg-name> [py-name]``

   * This tells ``pythy`` to create a Python class named ``py-name``.
   * For all C functions whose first parameter name is ``c-arg-name``,
     ``pythy`` will create a Python wrapper method within the
     associated Python class.
   * TODO: The location of this directive does not matter: it applies to
     all functions in all files.
   * If ``py-name`` is ommitted, Python will choose a nicely formatted
     Python class name based on ``c-arg-name``.
   * TODO: Should there be a way to override this for a particular
     function?
   * TODO: Should we use the parameter type instead of name?

#. ``init <c-arg-name> <c-func-name>``

   * This tells ``pythy`` to use the C function ``c-func-name``
     as the ``__init__`` function for the Python class created from
     ``c-arg-name``.
   * TODO: The locaton of this directive does not matter: as long as the
     given function and class exist in some file, this directive will
     apply.
   * At one point I thought we could do this purely by aliasing the
     function to ``__init__``, but it's first parameter doesn't have the
     right name, so it wouldn't work.

#. ``func_alias <c-func-name> <py-name>``

   * This causes ``pythy`` to rename the wrapper for ``c-func-name`` to
     ``py-name``.
   * TODO: The location of this wrapper does not matter. As long as
     ``c-func-name`` is declared somewhere in some file, ``pythy`` will
     rename it.

#. TODO: ``private [c-func-name]``

   * This prevents Python from creating a wrapper for the given C
     function (the next C function, if ``c-func-name`` is not given).
   * If ``c-func-name`` is given (and that function is declared in some
     file), the location of this directive does not matter. Otherwise,
     it will be applied to the immediately following function; if there
     is no following function in the same header file, ``pythy`` will
     raise an error.

#. TODO: byte-array length specification

#. TODO: specify property
