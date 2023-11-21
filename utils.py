from dataclasses import dataclass
from typing import Callable, Generic, Iterator, NoReturn, Optional, TypeVar


@dataclass
class Span:
    start: int
    end: int

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __add__(self, other: "Span") -> "Span":
        return Span(self.start, other.end)

    def __str__(self) -> str:
        return f"{self.start}..{self.end}"

    def index_source(self, source: str) -> str:
        return source[self.start : self.end]


T = TypeVar("T")


class Peekable(Generic[T]):
    """
    Wraps any `Iterator[T]` and provides a `peek` method that returns the current element without consuming it

    Note: This adapter does not throw `StopIteration` on the final element but rather returns `None`
    """

    head: Optional[T]
    iterator: Iterator[T]
    peeked: bool

    def __init__(self, iterator: Iterator[T]):
        self.head = None
        self.iterator = iterator
        self.peeked = False

    def peek(self) -> Optional[T]:
        if not self.peeked:
            self.peeked = True
            self.head = next(self.iterator, None)
        return self.head

    def __iter__(self) -> "Peekable[T]":
        return self

    def __next__(self) -> Optional[T]:
        if self.peeked:
            self.peeked = False
            return self.head
        else:
            return next(self.iterator, None)


U = TypeVar("U")


def map_pred(opt: Optional[U], f: Callable[[U], bool]) -> bool:
    if opt is None:
        return False
    else:
        return f(opt)


def stop_iteration() -> NoReturn:
    raise StopIteration
