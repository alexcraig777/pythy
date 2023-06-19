"""
Create a Python module to interface with a compiled library

Stages of processing
--------------------

1. Parse the header file (parse all directives and find all functions).
   - This stage creates many InterfaceFunction and InterfaceClass
     instances.

2. Create the actual internal Python classes and functions dynamically.
   - The classes are created using Python's `type` function.
   - The functions are loaded from the shared library using `backend.py`,
     which uses either `ctypes` or `sockapi.py`.
   - This stage also applies all necessary wrappers to the new Python
     functions.

3. Bind the classes and functions to the given module.
   - This stage also uses information from the header file to fill
     in fields that will generate nice pydocs for the functions.


Directives
----------

Directives are read from comment lines following a "$" character.

a. define <old-str> -> <new-str>
   - used to do text replacement
   - This is the only directive where the arguments can contain spaces.

b. class <c-arg-name> [py-name]
   - used to indicate that there's a Python class that will absorb
     some of the interface functions as methods
   - If `py-name` is ommitted, Python will choose a nicely formatted
     one based on `c-arg-name`.

c. init <cls-name> <func>
   - used to indicate that a function should be used as the __init__
     method for a class
   - At one point I thought we could do this purely by aliasing the
     function to "__init__", but it's first parameter doesn't have the
     right name, so it wouldn't work.

d. func_alias <c-name> <py-name>
   - used to specify an alternate Python name for a function

e. wrapper[_update] <wrapper-name> <patterns>
   - used to initialize (or update) a wrapper to apply to certain
     functions in the interface
   - see more under "Wrappers", below
   - the first wrapper directive for a wrapper must be `wrapper`; all
     following directives for the same wrapper must be `wrapper-update`.
   - <patterns> is a space-separated list of mini-regexes that will be
     used to determine what functions the wrapper should be applied to.
   - a mini-regex has the following format:
     - optional "!": ignore functions that match this pattern, instead
       of including them
     - optional "@": apply pattern to class name, instead of C name
     - The remainder is a list of sub-patterns, separated by "|", which
       are "or"ed together.
     - Each sub-pattern can contain regular characters and the speial
       character "*" to match any substring.
     - For class patterns only, the special character "#" indicates a
       class of "None" (i.e., the function does not belong in a class).
       All other positive class patterns will ignore functions that
       don't belong to a class. See the examples.

   - To determine whether to apply a given wrapper to a function, the
     program will apply each pattern from the list in order to the
     function (either it's C name or its class name, as determined by
     whether the pattern has a leading "@"). The default is not to
     apply it.

   - Examples:
     $ wrapper my_wrapper @#
     - This wrapper will be applied to all functions that are not in a
       class. An equivalent pattern list would be "* !@*" (in which the
       initial "*" means apply to all functions; the "!@*" means ignore
       functions whose class names match "*", which is all classes that
       exist).

     $ wrapper my_wrapper @*
     - This wrapper will be applied to all functions that are in a class.
       An equivalent pattern list would be "* !@#".

     $ wrapper my_wrapper interface_free_buffer
     - This wrapper matches only the function `interface_free_buffer`.

     $ wrapper my_wrapper * !interface_free_buffer
     - This wrapper matches all functions except `interface_free_buffer`.

Wrappers
--------

The Interface instance keeps track of all registered wrappers.

It automatically registers wrapper_init_method and wrapper_generic_method
(the ones that take care of methods in classes) in its __init__ method.

Other wrappers are added or modified as indicated by the header file.
"""

import keyword
import os
import types

from .regex import MiniRegex
from . import backend
from . import split
from . import variable
from . import wrappers as built_in_wrapper_module


class InterfaceFunction:
    """ A class representing functions in a Python-C interface """

    interface_prefix = "interface_"

    def __init__(self, prototype, doc):
        # Make sure parentheses look right.
        assert "(" in prototype
        assert prototype.endswith(");")
        assert ")" not in prototype[: -2]

        first_half, param_half = prototype[: -2].split("(")

        # Find the function's return type and C name.
        rtn_type_str, c_name = split.split_at_last_space(first_half)
        self.c_name = c_name
        self.rtn_type = variable.Type(rtn_type_str)

        # Parse out the parameters.
        # We need different C and Python parameter lists, because Python's
        # parameters will change (certainly for class methods).
        param_strings = [s.strip() for s in param_half.split(",")]
        self.c_params = [variable.Parameter(param_str) for param_str in param_strings]
        self.py_params = [variable.Parameter(str(param)) for param in self.c_params]

        assert self.c_name.startswith(self.interface_prefix)
        self.py_name = self.c_name.removeprefix(self.interface_prefix)

        ### Check for Python keywords.
        if keyword.iskeyword(self.py_name):
            raise ValueError("Function name '{}' is ".format(self.py_name) +
                             "a Python keyword")
        for param in self.py_params:
            if keyword.iskeyword(param.name):
                raise ValueError("Parameter name '{}' ".format(param.name) +
                                 "is a Python keyword")

        self.cls = None
        self.wrappers = []

        self.doc = doc

    def __str__(self):
        rtn = self.rtn_type.c_str + " " + self.c_name + "("
        rtn += ", ".join(str(param) for param in self.c_params)
        rtn += ")"

        rtn += " -> " + self.py_name + "("
        rtn += ", ".join(param.name for param in self.py_params)
        rtn += ")"

        return rtn

    def load_py_func(self, lib):
        """ Load the actual function from the library

        This uses the backend (ctypes or sockapi) selected by
        `backend.default_mode`. """
        arg_types = [param.type.c_type for param in self.c_params]
        self.py_func = lib.get_function(self.c_name,
                                        arg_types,
                                        self.rtn_type.c_type)

    def register_wrapper(self, wrapper):
        """ Register a wrapper to be applied later.

        Registered wrappers are applied in a FIFO order. """

        self.wrappers.append(wrapper)

    def apply_wrappers(self):
        """ Apply all registered wrappers.

        Wrappers are applied in the order they were registered. """

        for wrapper in reversed(self.wrappers):
            wrapper(self)

    def bind(self, module):
        """ Bind this function to its class, or `module`, if it has none.

        In either case, set `self.module` for use in pydocs. """

        if self.cls is None:
            setattr(module, self.py_name, self.py_func)
        else:
            setattr(self.cls.cls, self.py_name, self.py_func)

        self.module = module

    def set_up_pydoc(self):
        """ Set up the stuff required for producing a clean pydoc.

        A lot of this uses somewhat undocumented internals from the
        `inspect` module, which is used by pydoc to generate the
        documentation. """

        self.py_func.__name__ = self.py_name
        text_sig = "(" + ", ".join(param.name for param in self.py_params) + ")"
        self.py_func.__text_signature__ = text_sig

        self.py_func.__module__ = self.module.__name__

        self.py_func.__doc__ = self.doc

    def add_to_class(self, cls):
        """ Update to reflect that this function is a method of a class.

        For __init__ methods, it's essential that by this point the
        function's `py_name` be changed to "__init__". """

        self.cls = cls

        if self.py_name == "__init__":
            # This will take care of inserting the first "self" parameter.
            self.register_wrapper(built_in_wrapper_module.init_method)
        else:
            # This will take care of changing the first parameter name.
            self.register_wrapper(built_in_wrapper_module.generic_method)


class InterfaceClass:
    """ A class representing classes in a Python-C interface. """

    def __init__(self, c_name, py_name = None):
        self.c_name = c_name
        if py_name is None:
            self.py_name = c_name.capitalize()
        else:
            self.py_name = py_name
        self.funcs = []

    def __str__(self):
        rtn = "class {}".format(self.py_name)
        for func in self.funcs:
            rtn += "\n    " + str(func)
        return rtn

    def add_function(self, func):
        """ Add a function as a method of this class. """

        self.funcs.append(func)
        func.add_to_class(self)

    def create_py_class(self):
        """ Actually create the Python class. """

        self.cls = type(self.py_name, (), dict())

    def bind_to_module(self, module):
        """ Bind the class to `module` and set `self.module`. """

        setattr(module, self.py_name, self.cls)
        self.module = module

    def set_up_pydoc(self):
        """ Set up the stuff required for producing a clean pydoc.

        This is not responsible for setting up pydocs for its methods. """

        self.cls.__module__ = self.module.__name__


class Interface:
    """ A representation of a Python interface to a compiled library

    The main public methods are:
    - parse_header_file
    - create_internals
    - bind_to_module

    Once the interface has been bound to a Python module, it's no
    longer needed. """

    comment_marker = "//"
    directive_marker = "$"

    directives = {"define", "class", "init", "func_alias",
                  "wrapper", "wrapper_update"}

    def __init__(self, wrapper_modules = None):
        self.functions = []
        self.classes = dict()

        self.defines = []
        self.init_funcs = dict()
        self.func_aliases = dict()
        self.wrappers = []

        if wrapper_modules is None:
            self.wrapper_modules = [built_in_wrapper_module]
        else:
            self.wrapper_modules = wrapper_modules
            self.wrapper_modules.append(built_in_wrapper_module)

        self.current_doc = ""

    def parse_header_file(self, header_file):
        """ Parse a C header file.

        This reads all the directives and creates all the contained
        InterfaceFunctions and InterfaceClasses. """
        with open(header_file, "r") as f:
            while self.parse_logical_line(f):
                pass

    def create_internals(self, library_file):
        """ Actually create the internal Python classes and functions. """

        for cls in self.classes.values():
            cls.create_py_class()

        lib = backend.Backend(library_file)
        lib.open_library()
        for func in self.functions:
            # Load the function from the library.
            func.load_py_func(lib)

            # Register and apply all wrappers.
            for w in self.wrappers:
                if w.check_apply_to_function(func):
                    func.register_wrapper(w.func)

            func.apply_wrappers()

        # Create the cleanup function for the library.
        self.close = lib.close

    def bind_to_module(self, module):
        """ Create the necessary attributes of `module` and set up its pydoc. """
        for cls in self.classes.values():
            cls.bind_to_module(module)
        for func in self.functions:
            func.bind(module)

        for cls in self.classes.values():
            cls.set_up_pydoc()
        for func in self.functions:
            func.set_up_pydoc()

        # Bind the cleanup function to the module.
        module.close = self.close

    def parse_logical_line(self, f):
        """ Parse a logical line from the header file.

        This will digest multiple lines from the header file if a
        function prototype is split over multiple lines. """

        line = f.readline()
        if not line:
            return False

        ### First, check if this is a directive specifically for us.
        if line.startswith(self.comment_marker):
            if self.directive_marker in line:
                self.parse_directive_line(line)

            self.current_doc += line.removeprefix(self.comment_marker)

        else:
            line = self._strip_whitespace_and_comment(line)
            line = self._apply_defines(line)

            if "(" in line:
                # Continue reading lines will we've reached the final ");".
                while not line.endswith(");"):
                    ### Append the next line, approrpiately stripped.
                    next_line = f.readline()
                    if not next_line:
                        raise ValueError("File ended during function definition")

                    next_line = self._strip_whitespace_and_comment(next_line)
                    next_line = self._apply_defines(next_line)
                    line += " " + next_line

                self.parse_function_prototype(line)

            # Reset the current doc string we're tracking.
            self.current_doc = ""

        return True

    def parse_function_prototype(self, prototype):
        """ Parse a line that's a function prototype. """

        func = InterfaceFunction(prototype, self.current_doc.strip())
        cls = None

        # Check if this function has been given a specific alias and
        # apply it if necessary.
        self._apply_aliases(func)

        # Check if this function belongs to a class we know about,
        # or if it's just a normal function.
        if func.c_name in self.init_funcs:
            # If we're specifically listed as an init function, we know
            # where we belong.
            func.py_name = "__init__"
            cls = self.init_funcs.pop(func.c_name)

        elif func.c_params:
            ### Otherwise if our first parameter is the name of a class,
            ### we assume we belong with that class.
            if func.c_params[0].name in self.classes:
                cls = func.c_params[0].name

        # Add this function to the Interface's list of functions.
        # If it belongs to a class, also add it there.
        self.functions.append(func)
        if cls is not None:
            self.classes[cls].add_function(func)

    def parse_directive_line(self, line):
        """ Parse a line that's a directive to our interpreter. """

        directive_string = line[line.index(self.directive_marker) + 1:]
        directive_string = directive_string.strip()
        directive = directive_string[:directive_string.index(" ")]
        arg_string = directive_string.removeprefix(directive).strip()

        if directive not in self.directives:
            msg = "directive '{}' not understood".format(directive)
            raise ValueError(msg)

        method_name = "_handle_" + directive
        handle_method = getattr(self, method_name)
        handle_method(arg_string)

    def _handle_define(self, arg_string):
        old, new = arg_string.split("->")
        self.defines.append((old.strip(), new.strip()))

    def _handle_class(self, arg_string):
        args = arg_string.split()
        c_name = args[0]
        if len(args) == 2:
            py_name = args[1]
        else:
            py_name = None
        self.classes[c_name] = InterfaceClass(c_name, py_name)

    def _handle_init(self, arg_string):
        cls_name, func_name = arg_string.split()
        self.init_funcs[func_name] = cls_name

    def _handle_func_alias(self, arg_string):
        c_name, py_name = arg_string.split()
        self.func_aliases[c_name] = py_name

    def _handle_wrapper(self, arg_string):
        wrapper_name, *patterns = arg_string.split(" ")

        # Find the wrapper function referenced in one of the wrapper modules.
        for wrapper_mod in self.wrapper_modules:
            if hasattr(wrapper_mod, wrapper_name):
                wrapper_func = getattr(wrapper_mod, wrapper_name)
                break
        else:
            raise ValueError(f"Cannot find wrapper '{wrapper_name}'")
        mini_regexes = [MiniRegex(p) for p in patterns]
        self.wrappers.append(InterfaceFunctionWrapper(wrapper_name,
                                                      wrapper_func,
                                                      mini_regexes))

    def _handle_wrapper_update(self, arg_string):
        func_name, wrapper_name = arg_string.split()
        raise NotImplementedError()

    def _apply_defines(self, line):
        for old, new in self.defines:
            line = line.replace(old, new)

        return line

    def _apply_aliases(self, func):
        if func.c_name in self.func_aliases:
            func.py_name = self.func_aliases.pop(func.c_name)


    @classmethod
    def _strip_whitespace_and_comment(cls, line):
        """ Strip trailing whitespace and comments from a line. """

        if cls.comment_marker in line:
            line = line[: line.index(cls.comment_marker)]
        line = line.strip()
        return line


class InterfaceFunctionWrapper:
    """ A class that represents a wrapper function and patterns to
    choose which functions it applies to. """

    def __init__(self, name, func, mini_regexes):
        self.name = name
        self.func = func
        self.mini_regexes = mini_regexes

    def check_apply_to_function(self, interface_function):
        """ Check if we should apply this wrapper to `interface_function`.

        This is the result of checking if `interface_function` is accepted
        by each mini-regex, in order. """

        rtn = False

        for mini_regex in self.mini_regexes:
            result = mini_regex.check(interface_function)
            if result == MiniRegex.include:
                rtn = True
            elif result == MiniRegex.exclude:
                rtn = False

        return rtn


def create_interface(header_file, library_file,
                     module = None,
                     wrapper_modules = None):
    """ Load an interface from a C header file and shared library,
    and bind that interface to the Python module `module`.

    This is the main public function for the entire package. """

    interface = Interface(wrapper_modules = wrapper_modules)
    interface.parse_header_file(header_file)
    interface.create_internals(library_file)

    # Create a new empty module, if we weren't given one already.
    if module is None:
        name = os.path.basename(header_file)
        name = name[: name.rindex(".")]
        module = types.ModuleType(name)

    interface.bind_to_module(module)
    return module
