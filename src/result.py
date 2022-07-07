from dataclasses import dataclass
from typing import Any, Callable, Generic, ParamSpec, TypeAlias, TypeVar

from .interfaces import Binder, Foldable, Monad, UnwrapError, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
E = TypeVar("E")

Result: TypeAlias = "Ok[T, E] | Err[T, E]"
RHandle: TypeAlias = "Callable[[Result[T, E]], T]"


class RBinder(Binder["Err[T, E]"], Generic[T, E]):
    pass


@dataclass
class Ok(Monad, Unwrappable[T1], Foldable, Generic[T1, E]):
    _v: T1

    def __init__(self, v: T1):
        self._v = v

    def apply(self, f: Callable[[T1], "Result[T2, E]"]) -> "Result[T2, E]":
        return f(self._v)

    def fold(
        self, f: Callable[[T1, T2], Result[T1, E]], l: list[T2]
    ) -> "Result[T1, E]":
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


@dataclass
class Err(Monad, Unwrappable[T], Foldable, Generic[T, E]):
    _v: E

    def __init__(self, e: E):
        self._v = e

    def apply(self, _: Callable[..., Any]) -> "Err[T, E]":
        return self

    def fold(self, f: Callable[..., Any], l: list[Any]) -> "Err[T, E]":
        return self

    def __call__(self, handler: RHandle[T, E]) -> T:
        return handler(self)

    def ok(self) -> bool:
        return False

    def unwrap(self, d: T | None = None, /) -> T:
        if d is None:
            raise UnwrapError()
        else:
            return d
