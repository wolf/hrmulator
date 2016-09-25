"""
Memory in Human Resource Machine is represented as numbered tiles on the
floor.  They can also have textual labels.  If tile 5 is labeled 'hello', then
your program can `copy_to hello` and it will do the same thing as `copy_to 5`.
You make this happen with `label_tile`:

    >>> m = Memory()
    >>> m[5] = 74
    >>> m[5]
    74
    >>> m.label_tile(5, label='index') # keyword for demonstration only
    >>> m['index']
    74

You don't have to call `label_tile` individually for every label you wish to
apply.  You can label them all at once by passing in a dictionary at
`__init__` time.  E.g.,

    >>> m = Memory(labels={'index':5, 'zero':9})

You can put initial values onto the tiles as well:

    >>> m = Memory(
    ...     labels={'index':5, 'zero':9},
    ...     values={'index':74, 'zero':0}
    ... )
    >>> m['zero']
    0

Normally, this constructor is all you care about since the game predefines
the contents of memory, and you predefine the labels.  You don't otherwise
interact directly with memory, `Instruction`s do that.  Everything else is
useful to you in the debugger when you actually want to change things.

The Human Resource Machine also implements "indirect" memory access, so, for
instance, if memory tile 5 contains 74, you can get and set the value in
memory tile 74 _through_ tile 5, like so:

    >>> m.get('index')
    74
    >>> m.set('index', 'C', indirect=True)
    >>> m[74]
    'C'
    >>> m.get('index', indirect=True)
    'C'

Trying to indirect through a letter raises an exception, even if you happen to
have labeled a tile with that letter.  Sorry, but that's how the game works.
Example:

    >>> m.get(74, indirect=True)
    Traceback (most recent call last):
        ...
    hrmulator.Memory.CantIndirectThroughLetter: A letter does not address any tile.

The only things you can put onto a memory tile are integers and single characters (letters).

    >>> m['index'] = 3.14
    Traceback (most recent call last):
        ...
    hrmulator.Memory.CantStoreBadType: A memory tile may only hold an integer or a single character.

You are not allowed to read from an empty tile.  Sorry, but again---that's how
the game works:

    >>> m[3]
    Traceback (most recent call last):
        ...
    hrmulator.Memory.MemoryTileIsEmptyError: (3, 'Tile 3 is empty.')

Of course I don't support slices.  The game doesn't use them, so I don't need them.
"""
from collections import defaultdict, OrderedDict

import termcolor

from .Utilities import is_char, is_int_or_char, int_if_possible


class MemoryError(Exception):
    pass


class MemoryTileIsEmptyError(MemoryError):
    pass


class CantIndirectThroughLetter(MemoryError):

    def __init__(self):
        super().__init__('A letter does not address any tile.')


class CantStoreBadType(MemoryError):

    def __init__(self):
        super().__init__('A memory tile may only hold an integer or a single character.')


class Memory:
    """
    Implements the floor-tile storage-system from Human Resource Machine.

    Does this with two member variables: `tiles`, a dictionary of the actual
    values stored (dictionary because it's sparse); and `label_map` which maps
    names to indices.  The keys in the label map are all non-numeric strings.
    The values are all integers.  The keys in the `tiles` dictionary are all
    integers.

    For an end-user, the most important methods are the constructor, which
    allows them to construct memory with values and labels already in place;
    and `label_tile`, for labeling tiles after construction-time.  The getters
    and setters are really for use by Instructions.  `debug_print` is used by
    the debugger.
    """

    def __init__(self, labels=None, values=None):
        self.label_map = OrderedDict(labels or [])
        # label_map maps string label to integer tile-index.  Using
        # OrderedDict here ensures that debug_print will print multiple
        # labels on the same tile in the order which they were applied.
        # Yeah, I realize it's a ridiculous edge case.

        self.tiles = {}
        # the tiles themselves are sparse, so use a dictionary

        if values is not None:
            for k, v in values.items():
                self.__setitem__(k, v) # ensures we resolve initial labels

    def _resolve_key(self, key):
        """
        Turn a name or number into an integer index.

            _resolve_key(7) == 7        # can be the identity function
            _resolve_key('7') == 7      # fixes strings for you
            _resolve_key('a_label_for_tile_7') == 7
                                        # looks up labels
        """
        key = int_if_possible(key) # don't be fooled, '24' is not a label
        key = self.label_map.get(key, key)
        if type(key) is not int:
            raise KeyError(key,
                'The label "{}" has not been applied to any tile.'.format(key)
            )
        return key

    def label_tile(self, key, label):
        """So you can apply labels even after construction-time."""
        self.label_map[label] = self._resolve_key(key)

    def __getitem__(self, key):
        """A convenience method, [] for when access is not indirect."""
        value = self.tiles.get(self._resolve_key(key), None)
        if value is None:
            raise MemoryTileIsEmptyError(key, 'Tile {} is empty.'.format(key))
        return value

    def get(self, key, *, indirect=False):
        """
        General purpose: get a value from a tile whether it's indirect or not.

        ...because __getitem__ can't take an additional parameter.
        """
        value = self.__getitem__(key)
        if indirect:
            if is_char(value):
                raise CantIndirectThroughLetter()
            value = self.__getitem__(value)
            # use `__getitem__` so we check for MemoryTileIsEmptyError
        return value

    def __setitem__(self, key, value):
        """A convenience method, [] for when access is not indirect."""
        if not is_int_or_char(value):
            raise CantStoreBadType()
        self.tiles[self._resolve_key(key)] = value

    def set(self, key, value, *, indirect=False):
        """
        General purpose: set a value from a tile whether it's indirect or not.

        ...because __setitem__ can't take an additional parameter.
        """
        if not is_int_or_char(value):
            raise CantStoreBadType()
        key = self._resolve_key(key)
        # the index of the direct tile

        if indirect:
            key = self.__getitem__(key)
            # whose value is the index of the indirect tile

            if is_char(key):
                raise CantIndirectThroughLetter()
        self.tiles[key] = value

    def debug_print(self, key=None):
        """
        Print everything interesting on all the tiles; or else a single tile.

        Everything interesting is: every slot that has a value or a label, in
        order of indices.  Print the indices and labels in color, just like
        the program listing.
        """

        # invert the label map, so we can lookup labels by index
        labels = defaultdict(list)
        for label in self.label_map:
            labels[self.label_map[label]].append(label)

        def print_one(key):
            """Pretty-print a single key, its labels if any, and its value."""
            key = self._resolve_key(key)
            key_str = termcolor.colored('{:2d}'.format(key), 'blue')
            # print tile keys in color, just like in the program listing
            print(key_str, end='')

            if key in labels: # are there any labels for this index?
                separator = ''
                print('(', end='')
                for label in labels[key]:
                    print(separator, end='')
                    separator = ', '
                    print(termcolor.colored(label, 'blue'), end='')
                print(')', end='')
            print(': ', end='')
            try:
                value = self.tiles[key]
            except KeyError:
                print(termcolor.colored('empty', 'red'))
            else:
                if is_char(value):
                    print("'{}'".format(value))
                    # quote it
                else:
                    print(value)

        if key is None:
            # print everything
            all_indices = set(self.tiles.keys()).union(set(labels.keys()))
            for index in sorted(all_indices):
                print_one(index)
        else:
            print_one(key)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
