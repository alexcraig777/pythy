:tocdepth: 1

Processing Headers
===============================

These are the stages in which ``pythy`` processes header files:

#. Collect all function prototypes and directives.

   Before ``pythy`` does any real processing, it collects all the
   function prototypes and directives from all the header files. The
   only exception to this rule is ``define`` directives, which cause
   ``pythy`` to perform text substitution on the remainder of the
   current file.

   Collecting all prototypes and directives before any further
   processing allows ``pythy`` and developers the most flexibility in
   where directives are placed relative to prototypes. Most importantly,
   it makes the order in which header files are processed unimportant.

#. Remove private prototypes.

#. Create Python interface, applying directives as needed.

TODO
