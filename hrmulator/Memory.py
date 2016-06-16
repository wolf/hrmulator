class Memory:

    def __init__(self, labels=None, values=None):
        self.label_map = {} if labels is None else labels.copy()
        self.tiles = {}
        if values is not None:
            for k, v in values.items():
                self.__setitem__(k, v)

    def label_tile(self, i, label):
        k = self.label_map.get(i, i)
        self.label_map[label] = k

    def __getitem__(self, i):
        k = self.label_map.get(i, i)
        return self.tiles.get(k, None)

    def __setitem__(self, i, value):
        k = self.label_map.get(i, i)
        self.tiles[k] = value

    def __delitem__(self, i):
        k = self.label_map.get(i, i)
        del self.tiles[k]
