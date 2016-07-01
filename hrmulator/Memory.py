"""
Memory in Human Resource Machine is represented as numbered tiles on the
floor.  They can also have textual labels.  If tile 5 is labeled 'hello', then
your program can `copy_to [hello]` and it will do the same thing as
`copy_to [5]`.  You make this happen with:

        memory.label_tile(5, 'hello')
        memory['hello'] = 74

Here, I implement the simplest thing that can reasonably work.  Note that I
don't support slices at all (of course).

You don't have to call `label_tile` individually for every label you wish to
apply.  You can label them all at once by passing in a dictionary at
`__init__` time.  E.g.,

        memory = Memory(labels={'hello':5, 'zero':9})

You can put initial values onto the tiles as well:

        memory = Memory(
            labels={'hello':5, 'zero':9},
            values={'zero':0, 5:'A'}
        )

        assert(memory['hello'] == 'A')
"""


class MemoryError(Exception):
    pass


class MemoryTileIsEmptyError(MemoryError):
    pass


class Memory:

    def __init__(self, labels=None, values=None):
        self.label_map = {} if labels is None else labels.copy()
            # label_map maps string label : to integer tile index

        self.tiles = {}
            # the tiles themselves are sparse, so use a dictionary

        if values is not None:
            for k, v in values.items():
                self.__setitem__(k, v) # ensures we resolve initial labels

    def resolve_key(self, key):
        key = self.label_map.get(key, key)
        if type(key) is not int:
            raise KeyError(key,
                'The label "{}" has not been applied to any tile.'.format(key)
            )
        return key

    def label_tile(self, key, label):
        self.label_map[label] = self.resolve_key(key)

    def __getitem__(self, key):
        value = self.tiles.get(self.resolve_key(key), None)
        if value is None:
            raise MemoryTileIsEmptyError(key, 'Tile {} is empty.'.format(key))
        return value

    def get(self, key, *, indirect=False):
        value = self.__getitem__(key)
        if indirect:
            value = self.__getitem__(value)
        return value

    def __setitem__(self, key, value):
        self.tiles[self.resolve_key(key)] = value

    def set(self, key, value, *, indirect=False):
        key = self.resolve_key(key)
        if indirect:
            key = self.resolve_key(self.__getitem__(key))
        self.tiles[key] = value

    def __delitem__(self, key):
        del self.tiles[self.resolve_key(key)]
