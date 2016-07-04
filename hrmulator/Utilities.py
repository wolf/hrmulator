"""
Utility routines used in more than one spot.
"""

def is_char(value):
    return type(value)==str and len(value)==1


def is_int_or_char(value):
    return type(value)==int or is_char(value)


def int_if_possible(value):
    try:
        return int(value)
    except ValueError:
        return value
