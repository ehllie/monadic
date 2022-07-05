from dataclasses import dataclass
from functools import reduce, wraps
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    ParamSpec,
    Protocol,
    Type,
    TypeVar,
    cast,
)

from interfaces import Foldable, Monad, Unwrappable

P = ParamSpec("P")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
E = TypeVar("E", bound=Exception)


class Result(Monad[T1], Unwrappable[T1], Foldable[T1], Protocol[T1, E]):
    def apply(self, f: Callable[[T1], "Result[T2, E]"], /) -> "Result[T2, E]":  # type: ignore
        ...

    def fold(self, f: Callable[[T1, T2], "Result[T1, E]"], i: Iterable[T2]) -> "Result[T1, E]":  # type: ignore
        ...

    def inst(self) -> "Ok[T1, E] | Err[E]":
        ...

    @classmethod
    def binds(cls, f: Callable[P, T1], /) -> Callable[P, "Result[T1, E]"]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> "Result[T1, E]":
            try:
                return Ok[T1, E](f(*args, **kwargs))
            except Err as err:  # type: ignore
                return cast(Err[E], err)

        return inner

    @classmethod
    def capture(
        cls, err_type: Type[E]
    ) -> Callable[[Callable[P, T1]], Callable[P, "Result[T1, E]"]]:
        def wrapper(f: Callable[P, T1], /):
            @cls.binds
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> T1:
                try:
                    return f(*args, **kwargs)
                except err_type as err:
                    raise Err[E](err)

            return inner

        return wrapper


@dataclass
class Ok(Result[T1, E], Generic[T1, E]):
    v: T1

    def __init__(self, v: T1):
        self.v = v

    def inst(self) -> "Ok[T1, E]":
        return self

    def apply(self, f: Callable[[T1], Result[T2, E]]) -> Result[T2, E]:
        return f(self.v)

    def fold(
        self, f: Callable[[T1, T2], Result[T1, E]], i: Iterable[T2]
    ) -> "Result[T1, E]":
        return reduce(lambda acc, x: acc.apply(lambda a: f(a, x)), i, self)

    def __call__(self, _: T1 | None = None) -> T1:
        return self.v

    def ok(self) -> bool:
        return True


@dataclass
class Err(Result[Any, E], Generic[E], Exception):
    e: E

    def __init__(self, e: E):
        self.e = e
        self.e_type = type(e)

    def inst(self) -> "Err[E]":
        return self

    def apply(self, _: Callable[..., Result[T2, E]]) -> Result[T2, E]:
        return self

    def fold(
        self, f: Callable[[T1, T2], Result[T1, E]], i: Iterable[T2]
    ) -> Result[T1, E]:
        return self

    def __call__(self, d: T1 | None = None) -> T1:
        if d is None:
            raise self
        else:
            return d

    def ok(self) -> bool:
        return False
