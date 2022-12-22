from petitparser.context import Context, Result
from petitparser.parser import Parser

class CharacterParser(Parser):
    __slots__ = '_predicate', '_message'

    def __init__(self, predicate, message: str):
        self._predicate = predicate
        self._message = message

    def parse_on(self, context: Context):
        buffer = context.buffer
        position = context.position

        if position < len(buffer) and self._predicate(buffer[position]):
            return context.success(buffer[position], position + 1)
        return context.failure(self._message)

    def fast_parse_on(self, buffer: str, position: int):
        if position < len(buffer) and self._predicate(buffer[position]):
            return position + 1
        return -1

    def neg(self, message: str = None):
        if message is None:
            message = 'not ' + self._message
        return CharacterParser(lambda x: not self._predicate(x), message)

    def has_equal_properties(self, other: Parser):
        return (super().has_equal_properties(other)
                and self._predicate == other._predicate
                and self._message == other._message)

    def copy(self):
        return CharacterParser(self._predicate, self._message)

    def __str__(self):
        return super().__str__() + '[' + self._message + ']'


class EpsilonParser(Parser):
    def parse_on(self, context: Context):
        return context.success(None)

    def fast_parse_on(self, buffer: str, position: int):
        return position

    def copy(self):
        return EpsilonParser()


class FailureParser(Parser):
    __slots__ = '_message',

    def __init__(self, message: str):
        self._message = message

    def parse_on(self, context: Context):
        return context.failure(self._message)

    def fast_parse_on(self, buffer: str, position: int):
        return -1

    def has_equal_properties(self, other: Parser):
        return (super().has_equal_properties(other)
                and self._message == other._message)

    def copy(self):
        return FailureParser(self._message)

    def __str__(self):
        return super().__str__() + '[' + self._message + ']'


class StringParser(Parser):
    __slots__ = '_size', '_predicate', '_message'

    def __init__(self, size: int, predicate, message: str):
        self._size = size
        self._predicate = predicate
        self._message = message

    def parse_on(self, context: Context):
        buffer = context.buffer
        start = context.position

        stop = start + self._size
        if stop <= len(buffer):
            result = buffer[start:stop]
            if self._predicate(result):
                return context.success(result, stop)
        return context.failure(self._message)

    def fast_parse_on(self, buffer: str, position: int):
        stop = position + self._size
        if stop <= len(buffer) and self._predicate(buffer[position:stop]):
            return stop
        else:
            return -1

    def has_equal_properties(self, other: Parser):
        return (super().has_equal_properties(other)
                and self._size == other._size
                and self._predicate == other._predicate
                and self._message == other._message)

    def copy(self):
        return StringParser(self._size, self._predicate, self._message)

    def __str__(self):
        return super().__str__() + '[' + self._message + ']'
