from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, ParamSpec, Protocol, TypeAlias, TypeVar

from .interfaces import Foldable, Monad, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
CO = TypeVar("CO", covariant=True)

MyBe: TypeAlias = "Just[T] | Nothing"


class Maybe(Monad[T1], Unwrappable[T1], Foldable[T1], Protocol[T1]):
    def apply(self, f: Callable[[T1], "MyBe[CO]"], /) -> "MyBe[CO]":  # type: ignore
        ...

    def fold(self, f: Callable[[T1, T2], "MyBe[T1]"], l: list[T2]) -> "MyBe[T1]":  # type: ignore
        ...

    @classmethod
    def binds(cls, f: Callable[P, T1 | None], /) -> Callable[P, "MyBe[T1]"]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> "MyBe[T1]":
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

    def apply(self, f: Callable[[T1], "MyBe[CO]"]) -> "MyBe[CO]":
        return f(self.v)

    def fold(self, f: Callable[[T1, T2], "MyBe[T1]"], l: list[T2]) -> "MyBe[T1]":
        match l:
            case []:
                return self
            case xs:
                return self.apply(lambda v: f(v, xs[0])).fold(f, xs[1:])

    def __call__(self, _: T1 | None = None) -> T1:
        return self.v

    def ok(self) -> bool:
        return True

    def __eq__(self, o: object) -> bool:
        match o:
            case Just(v):  # type: ignore
                if isinstance(v, type(self.v)):
                    return self.v == v
                return False
            case _:
                return False


class Nothing(Maybe[Any], Exception):
    def __init__(self):
        pass

    def apply(self, _: Callable[..., "MyBe[CO]"]) -> "MyBe[CO]":
        return self

    def fold(self, f: Callable[[T1, T2], "MyBe[T1]"], l: list[T2]) -> "MyBe[T1]":
        return self

    def __call__(self, d: T1 | None = None) -> T1:
        if d is None:
            raise self
        else:
            return d

    def ok(self) -> bool:
        return False

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Nothing):
            return True
        else:
            return False
