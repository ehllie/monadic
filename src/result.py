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
    v: T1

    def __init__(self, v: T1):
        self.v = v

    def apply(self, f: Callable[[T1], "Result[T2, E]"]) -> "Result[T2, E]":
        return f(self.v)

    def fold(
        self, f: Callable[[T1, T2], Result[T1, E]], l: list[T2]
    ) -> "Result[T1, E]":
        match l:
            case []:
                return self
            case xs:
                return self.apply(lambda v: f(v, xs[0])).fold(f, xs[1:])

    def __call__(self, _: Any) -> T1:
        return self.v

    def ok(self) -> bool:
        return True

    def unwrap(self, _: T1 | None = None, /) -> T1:
        return self.v

    def __eq__(self, o: object) -> bool:
        match o:
            case Ok(v):  # type: ignore
                if isinstance(v, type(self.v)):
                    return self.v == v
                return False
            case _:
                return False


@dataclass
class Err(Monad, Unwrappable[T], Foldable, Generic[T, E]):
    e: E

    def __init__(self, e: E):
        self.e = e

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

    def __eq__(self, o: object) -> bool:
        match o:
            case Err(e):  # type: ignore
                if isinstance(e, type(self.e)):
                    return self.e == e
                return False
            case _:
                return False
