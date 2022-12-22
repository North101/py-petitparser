from ..parser.primitive import EpsilonParser, FailureParser
from ..parser import Parser


def epsilon():
    return EpsilonParser()


def fail(message: str = 'impossible'):
    return FailureParser(message)
