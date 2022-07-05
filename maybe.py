from dataclasses import dataclass
from functools import reduce, wraps
from typing import Any, Callable, Generic, Iterable, ParamSpec, Protocol, TypeVar

from interfaces import Foldable, Monad, Unwrappable

P = ParamSpec("P")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
CO = TypeVar("CO", covariant=True)


class Maybe(Monad[T1], Unwrappable[T1], Foldable[T1], Protocol[T1]):
    def apply(self, f: Callable[[T1], "Maybe[CO]"], /) -> "Maybe[CO]":  # type: ignore
        ...

    def fold(self, f: Callable[[T1, T2], "Maybe[T1]"], i: Iterable[T2]) -> "Maybe[T1]":  # type: ignore
        ...

    def inst(self) -> "Just[T1] | Nothing":
        ...

    @classmethod
    def binds(cls, f: Callable[P, T1 | None], /) -> Callable[P, "Maybe[T1]"]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> "Maybe[T1]":
            try:
                match f(*args, **kwargs):
                    case None:
                        return Nothing()
                    case val:
                        return Just(val)
            except Nothing:
                return Nothing()

        return inner


@dataclass
class Just(Maybe[T1], Generic[T1]):
    v: T1

    def __init__(self, v: T1):
        self.v = v

    def inst(self) -> "Just[T1]":
        return self

    def apply(self, f: Callable[[T1], Maybe[CO]]) -> Maybe[CO]:
        return f(self.v)

    def fold(self, f: Callable[[T1, T2], Maybe[T1]], i: Iterable[T2]) -> Maybe[T1]:
        return reduce(lambda acc, x: acc.apply(lambda a: f(a, x)), i, self)

    def __call__(self, _: T1 | None = None) -> T1:
        return self.v

    def ok(self) -> bool:
        return True


class Nothing(Maybe[Any], Exception):
    def __init__(self):
        pass

    def inst(self) -> "Nothing":
        return self

    def apply(self, _: Callable[..., Maybe[CO]]) -> Maybe[CO]:
        return self

    def fold(self, f: Callable[[T1, T2], Maybe[T1]], i: Iterable[T2]) -> Maybe[T1]:
        return self

    def __call__(self, d: T1 | None = None) -> T1:
        if d is None:
            raise self
        else:
            return d

    def ok(self) -> bool:
        return False
