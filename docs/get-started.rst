:tocdepth: 1

Get Started
===========

Install ``pythy``
-----------------

.. code-block:: bash

    pip install pythy

Create your interface header file
---------------------------------

Create the header file ``add.h`` with the following contents:

.. code-block:: c

    int interface_add(int a, int b);

Create your compiled shared object
----------------------------------

#.  Create the C source-code file ``add.c`` with the following
    contents:

    .. code-block:: c

        #include "add.h"

        int interface_add(int a, int b) {
            return a + b;
        }

#.  Compile ``add.c`` into a Linux shared object file by running

    .. code-block:: bash

        gcc -fPIC -shared add.c -o add.so

    This should create a file ``add.so``.

Use ``pythy`` to call your compiled code from Python
----------------------------------------------------

Now this Python code will run your compiled code (you must run this
from the directory containing ``add.so`` and ``add.h``, or use correct
paths to those files):

.. code-block:: python

    import pythy

    adder = pythy.create_interface("add.h", "add.so")
    print(adder.add(1, 2))
