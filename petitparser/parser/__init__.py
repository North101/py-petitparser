from ..context import Context, Result


class Parser:
    __slots__ = ()

    def parse_on(self, context: Context):
        raise NotImplementedError(type(self))

    def fast_parse_on(self, buffer: str, position: int):
        res = self.parse_on(Context(buffer, position))
        return res.position if res.is_success else -1

    def parse(self, inp: str):
        return self.parse_on(Context(inp, 0))

    def accept(self, inp: str):
        return self.fast_parse_on(inp, 0) >= 0

    def matches(self, inp: str):
        from .. import character
        l = []
        self.and_().map_with_side_effects(l.append).seq(character.any()).or_(character.any()).star()\
            .fast_parse_on(inp, 0)
        return l

    def matches_skipping(self, inp: str):
        from .. import character
        l = []
        self.map_with_side_effects(l.append).or_(character.any()).star()\
            .fast_parse_on(inp, 0)
        return l

    def optional(self, otherwise = None):
        from .combinators import OptionalParser
        return OptionalParser(self, otherwise)

    def star(self):
        return self.repeat(0, -1)

    def star_greedy(self, limit):
        return self.repeat_greedy(limit, 0, -1)

    def star_lazy(self, limit):
        return self.repeat_lazy(limit, 0, -1)

    def plus(self):
        return self.repeat(1, -1)

    def plus_greedy(self, limit):
        return self.repeat_greedy(limit, 1, -1)

    def plus_lazy(self, limit):
        return self.repeat_lazy(limit, 1, -1)

    def repeat(self, min: int, max: int):
        from .repeating import PossesiveRepeatingParser
        return PossesiveRepeatingParser(self, min, max)

    def repeat_greedy(self, limit, min: int, max: int):
        from .repeating import GreedyRepeatingParser
        return GreedyRepeatingParser(self, limit, min, max)

    def repeat_lazy(self, limit, min: int, max: int):
        from .repeating import LazyRepeatingParser
        return LazyRepeatingParser(self, limit, min, max)

    def times(self, count: int):
        return self.repeat(count, count)

    def seq(self, *others):
        from .combinators import SequenceParser
        return SequenceParser(self, *others)

    def or_(self, *others):
        from .combinators import ChoiceParser
        return ChoiceParser(self, *others)

    def and_(self):
        from .combinators import AndParser
        return AndParser(self)

    def call_cc(self, handler):
        from .actions import ContinuationParser
        return ContinuationParser(self, handler)

    def not_(self, message: str = 'unexpected'):
        from .combinators import NotParser
        return NotParser(self, message)

    def neg(self, message: str = None):
        from .. import character
        if message is None:
            message = f'{self} not expected'

        return self.not_(message).seq(character.any()).pick(1)

    def flatten(self, message: str = None):
        from .actions import FlattenParser
        return FlattenParser(self, message)

    def token(self):
        from .actions import TokenParser
        return TokenParser(self)

    def trim(self, before = None, after = None):
        from .. import character
        from .actions import TrimmingParser
        if before is None:
            before = character.whitespace()

        if after is None:
            after = before

        return TrimmingParser(self, before, after)

    def end(self, message: str = 'end of input expected'):
        from .combinators import SequenceParser, EndOfInputParser
        return SequenceParser(self, EndOfInputParser(message)).pick(0)

    def settable(self):
        from .combinators import SettableParser
        return SettableParser(self)

    def map(self, func):
        from .actions import ActionParser
        return ActionParser(self, func)

    def map_with_side_effects(self, func):
        from .actions import ActionParser
        return ActionParser(self, func, True)

    def pick(self, index: int):
        return self.map(lambda x: x[index])

    def permute(self, *indexes: int):
        return self.map(lambda x: [x[i] for i in indexes])

    def separated_by(self, separator):
        from .combinators import SequenceParser

        def _m(res):
            result = [res[0]]
            for elem in res[1]:
                result.extend(elem)
            return result
        return SequenceParser(self, SequenceParser(separator, self).star()).map(_m)

    def delimited_by(self, separator):
        def _m(res):
            result = list(res[0])
            if res[1] is not None:
                result.append(res[1])
            return result
        return self.separated_by(separator).seq(separator.optional()).map(_m)

    def copy(self):
        raise NotImplementedError()

    def is_equal_to(self, other, seen: set = None):
        if seen is None:
            seen = set()

        if self == other or self in seen:
            return True

        return type(self) is type(other) and self.has_equal_properties(other) and self.has_equal_children(other, seen)

    def has_equal_properties(self, other):
        return True

    def has_equal_children(self, other, seen: set):
        selfChildren = self.get_children()
        otherChildren = self.get_children()

        if len(selfChildren) != len(otherChildren):
            return False

        for i in range(len(selfChildren)):
            if not selfChildren[i].is_equal_to(otherChildren[i], seen):
                return False

        return True

    def get_children(self):
        return []

    def replace(self, source, target):
        pass

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__ + '(' + ', ' .join(f'{k}={getattr(self, k)}' for k in _resolve_slots(type(self))) + ')'

    def __and__(self, other):
        return self.seq(other)

    def __or__(self, other):
        if other is None:
            return self.optional()
        else:
            return self.or_(other)

    def __getitem__(self, s):
        if isinstance(s, int):
            low = high = s
        elif isinstance(s, slice):
            low = s.start or 0
            high = s.stop or -1
        else:
            raise TypeError(type(s))
        return self.repeat(low, high)

    def __neg__(self):
        return self.not_()

    def __pos__(self):
        return self.and_()

    def deep_copy(self):
        copy = self.copy()
        for child in copy.get_children():
            copy.replace(child, child.deep_copy())
        return copy


def _resolve_slots(entry):
    if not hasattr(entry, '__slots__'):
        return ()
    res = []
    for b in entry.__bases__:
        res.extend(_resolve_slots(b))
    res.extend(entry.__slots__)
    return tuple(res)
