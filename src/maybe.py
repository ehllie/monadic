from dataclasses import dataclass
from typing import Any, Callable, Generic, ParamSpec, TypeAlias, TypeVar

from .interfaces import Binder, Foldable, Monad, UnwrapError, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
CO = TypeVar("CO", covariant=True)

Maybe: TypeAlias = "Just[T] | Nothing[T]"
MHandle: TypeAlias = "Callable[[Maybe[T]], T]"


class MBinder(Binder["Nothing[T]"], Generic[T]):
    pass


@dataclass
class Just(Monad, Unwrappable[T1], Foldable, Generic[T1]):
    _v: T1

    def __init__(self, v: T1):
        self._v = v

    def apply(self, f: Callable[[T1], "Maybe[CO]"]) -> "Maybe[CO]":
        return f(self._v)

    def fold(self, f: Callable[[T1, T2], "Maybe[T1]"], l: list[T2]) -> "Maybe[T1]":
        match l:
            case []:
                return self
            case xs:
                return self.apply(lambda v: f(v, xs[0])).fold(f, xs[1:])

    def __call__(self, _: Any) -> T1:
        return self._v

    def ok(self) -> bool:
        return True

    def unwrap(self, _: T1 | None = None, /) -> T1:
        return self._v


class Nothing(Monad, Unwrappable[T], Foldable, Generic[T]):
    def __init__(self):
        self._v = None

    def apply(self, _: Callable[..., Any]) -> "Nothing[T]":
        return self

    def fold(self, f: Callable[..., Any], l: list[Any]) -> "Nothing[T]":
        return self

    def __call__(self, handler: "MHandle[T]") -> T:
        return handler(self)

    def ok(self) -> bool:
        return False

    def unwrap(self, d: T | None = None, /) -> T:
        if d is None:
            raise UnwrapError()
        else:
            return d
