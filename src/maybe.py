from dataclasses import dataclass
from typing import Any, Callable, Generic, ParamSpec, TypeAlias, TypeVar

from .interfaces import UW, Foldable, Monad, UnwrapError, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
CO = TypeVar("CO", covariant=True)

Maybe: TypeAlias = "Just[T] | Nothing"
MH: TypeAlias = "Callable[[Maybe[T]], T]"


class MU(UW["Maybe[Any]", T], Generic[T]):
    pass


@dataclass
class Just(Monad, Unwrappable[T1], Foldable, Generic[T1]):
    v: T1

    def __init__(self, v: T1):
        self.v = v

    def apply(self, f: Callable[[T1], "Maybe[CO]"]) -> "Maybe[CO]":
        return f(self.v)

    def fold(self, f: Callable[[T1, T2], "Maybe[T1]"], l: list[T2]) -> "Maybe[T1]":
        match l:
            case []:
                return self
            case xs:
                return self.apply(lambda v: f(v, xs[0])).fold(f, xs[1:])

    def __call__(self, _: Any) -> T1:
        return self.v

    def ok(self) -> bool:
        return True

    def unwrap(self, d: T1 | None = None, /) -> T1:
        return self.v

    def __eq__(self, o: object) -> bool:
        match o:
            case Just(v):  # type: ignore
                if isinstance(v, type(self.v)):
                    return self.v == v
                return False
            case _:
                return False


class Nothing(Monad, Unwrappable[Any], Foldable):
    def __init__(self):
        pass

    def apply(self, _: Callable[..., Any]) -> "Nothing":
        return self

    def fold(self, f: Callable[..., Any], l: list[Any]) -> "Nothing":
        return self

    def __call__(self, handler: "MH[T]") -> T:
        return handler(self)

    def ok(self) -> bool:
        return False

    def unwrap(self, d: T | None = None, /) -> T:
        if d is None:
            raise UnwrapError()
        else:
            return d

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Nothing):
            return True
        else:
            return False
