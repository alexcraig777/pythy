""" Miniature regular expressions for evaluating whether to apply
a given wrapper to a given interface function """


import re


class MiniRegex:
    include = 0
    exclude = 1
    abstain = 2

    def __init__(self, pattern):
        self.pattern = pattern

    def check(self, interface_function):
        """ Check if `interface_function` is explicitly included,
        excluded, or not mentioned by this mini-regex.

        Returns either `MiniRegex.include`, `MiniRegex.exclude`, or
        `MiniRegex.abstain`. """
        return MiniRegex._check_pattern_against_func(interface_function,
                                                     self.pattern)

    @staticmethod
    def _check_pattern_against_func(interface_function, pattern):
        """ Perform internals of self.check. """
        if pattern.startswith("!"):
            positive_pattern = pattern.removeprefix("!")
            rtn = MiniRegex._check_pattern_against_func(interface_function,
                                                        positive_pattern)
            rtn = MiniRegex._negate(rtn)

        else:
            if pattern.startswith("@"):
                value = interface_function.cls.c_name
                pattern = pattern.removeprefix("@")
            else:
                value = interface_function.c_name

            result = MiniRegex._check_pattern_against_value(value, pattern)
            if result:
                rtn = MiniRegex.include
            else:
                rtn = MiniRegex.abstain

        return rtn

    @staticmethod
    def _check_pattern_against_value(value, pattern):
        """ Return True if `value` matches `pattern`; False otherwise. """

        subpatterns = pattern.split("|")
        rtn = any(MiniRegex._match_subpattern(value, subpattern)
                  for subpattern in subpatterns)
        return rtn


    @staticmethod
    def _match_subpattern(value, subpattern):
        """ Return True if `value` matches `subpattern`; False otherwise.

        `subpattern` can be either an expression that contains
        normal characters and "*", or "#".
        `value` can be either a string or `None`. """

        if subpattern == "#":
            if value is None:
                rtn = True
            else:
                rtn = False

        else:
            subpattern = subpattern.replace("*", ".*")
            subpattern += "$"
            compiled = re.compile(subpattern)
            if compiled.match(value) is not None:
                rtn = True
            else:
                rtn = False

        return rtn

    @staticmethod
    def _negate(check_result):
        """ Swap include <-> exclude; leave abstain. """
        swap_dict = {MiniRegex.include: MiniRegex.exclude,
                     MiniRegex.exclude: MiniRegex.include,
                     MiniRegex.abstain: MiniRegex.abstain}
        return swap_dict[check_result]
