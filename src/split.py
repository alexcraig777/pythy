""" Split strings """

def split_at_last_space(string):
    """ Split the string into 2 pieces around the last space.

    This is handy for splitting a string that was used to specify a
    C parameter into type and name. """

    space_idx = string.rfind(" ")
    if space_idx == -1:
        raise ValueError("'{}' contains no space".format(string))
    else:
        return string[:space_idx], string[space_idx + 1:]
