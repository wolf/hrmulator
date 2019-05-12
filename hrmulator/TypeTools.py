"""
Utility routines used in more than one spot.

`is_char` is used by Memory, Instructions, and Debugger to test for
incompatible types.

    >>> is_char(42)
    False
    >>> is_char("Hello, World!")
    False
    >>> is_char('A')
    True

`is_int_or_char` is used by Memory in its setters to prevent bad types from
getting onto the tiles.

    >>> is_int_or_char('A')
    True
    >>> is_int_or_char(43)
    True
    >>> is_int_or_char(True)
    False
    >>> is_int_or_char('52')
    False
    >>> is_int_or_char(int_if_possible('52'))
    True

`int_if_possible` prevents label mishaps for the private method
Memory._resolve_key.

    >>> int_if_possible(5)
    5
    >>> int_if_possible(True)
    True
    >>> int_if_possible('5')
    5
    >>> int_if_possible('5hello')
    '5hello'
    >>> int_if_possible('51.2')
    '51.2'
    >>> int_if_possible(51.2)
    51.2
"""


from typing import Any


def is_char(value: Any) -> bool:
    """Return True for strings of length 1."""
    return type(value) == str and len(value) == 1


def is_int_or_char(value: Any) -> bool:
    """Return True if the value is suitable for putting on a memory tile."""
    return type(value) == int or is_char(value)


def int_if_possible(value: Any) -> Any:
    """
    Convert an int or a str to an int.  Do not convert any other types.

    This is used to resolve the difference between labels and indices when the
    value in question came from `input()`.
    """
    try:
        if type(value) == str:
            return int(value)
    except ValueError:
        pass
    return value
