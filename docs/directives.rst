:tocdepth: 1

Directive Reference
===================

#. ``define <old-str> -> <new-str>``

   * This tells ``pythy`` to perform text replacement on the file
     contents before parsing it.
   * Each ``define`` directive only affects text *following it in the
     same file*.
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
   * If ``py-name`` is ommitted, ``pythy`` will choose a nicely
     formatted Python class name based on ``c-arg-name``.
   * TODO: Should there be a way to override this for a particular
     function?
   * TODO: We should use the parameter type instead of name.

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
   * TODO: The C function will have to return a pointer to the type
     associated with the class. So once we transition to using parameter
     type instead of name for classes we can drop the ``c-arg-name``
     argument to the directive.

#. ``func_alias <c-func-name> <py-name>``

   * This causes ``pythy`` to rename the wrapper for ``c-func-name`` to
     ``py-name``.
   * TODO: The location of this wrapper does not matter. As long as
     ``c-func-name`` is declared somewhere in some file, ``pythy`` will
     rename it.

#. TODO: ``private <c-func-name>``

   * This prevents Python from creating a wrapper for the given C
     function (the next C function, if ``c-func-name`` is not given).
   * TODO: Allow implied ``c-func-name``.
   * If ``c-func-name`` is given, the location of this directive does
     not matter. Otherwise, ``pythy`` will apply this directive to the
     immediately following function.
   * If ``c-func-name`` is given and the function does not exist, or if
     it is ommitted and there is no following function in the same
     header file, ``pythy`` will raise an error.

#. TODO: ``len <c-func-name>.<c-arg-name> <py-expression>``

   * This tells ``pythy`` how many known-size units a returned pointer
     points to.
   * TODO: Allow implied ``c-func-name``.
   * If ``c-func-name`` is given, the location of this directive does
     not matter. Otherwise, ``pythy`` will apply this directive to the
     immediately following function.
   * If ``c-func-name`` is given and the function does not exist, or if
     it is ommitted and there is no following function in the same
     header file, ``pythy`` will raise an error. If the C function does
     not have an argument named ``c-arg-name``, ``pythy`` will also
     raise an error.
   * The primary use case is for returning raw binary data that may
     contain internal zero bytes (e.g., reading debuggee memory).
   * ``py-expression`` must be a valid Python expression that evaluates
     to an integer. It may only reference integer-valued arguments
     passed to the function.
   * Is this really necessary?

#. TODO: ``property <property-name>``
