from ..parser.primitive import EpsilonParser, FailureParser


def epsilon():
    return EpsilonParser()


def fail(message: str = 'impossible'):
    return FailureParser(message)
