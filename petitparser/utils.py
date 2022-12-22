from .parser import Parser


class ParserIterator:
    def __init__(self, root):
        self._todo = [root]
        self._seen = {root}

    def __next__(self):
        if not self._todo:
            raise StopIteration
        current = self._todo.pop()
        for p in current.get_children():
            if p not in self._seen:
                self._todo.append(p)
                self._seen.add(p)
        return current


class Mirror:
    def __init__(self, parser):
        self._parser = parser

    def __str__(self):
        return type(self).__name__ + ' of ' + str(self._parser)

    def __iter__(self):
        return ParserIterator(self._parser)

    def transform(self, transformer):
        mapping = {p: transformer(p.copy()) for p in self}

        seen = set(mapping.values())
        todo = list(mapping.values())

        while todo:
            parent = todo.pop()
            for child in parent.get_children():
                if child in mapping:
                    parent.replace(child, mapping[child])
                elif child not in seen:
                    seen.add(child)
                    todo.append(child)
        return mapping[self._parser]
