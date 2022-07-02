from dataclasses import dataclass
from functools import reduce, wraps
from typing import Callable, Generic, Iterable, ParamSpec, Protocol, Type, TypeVar, cast

from interfaces import Foldable, Monad, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
_E = TypeVar("_E", bound=Exception)
E = TypeVar("E", bound=Exception)
CO = TypeVar("CO", covariant=True)


@dataclass
class Ok(Generic[T]):
    v: T


@dataclass
class Er(Generic[E]):
    e: E


class ResultType(Monad[T1], Unwrappable[T1], Foldable[T1], Protocol[T1, E]):
    value: Ok[T1] | Er[E]

    def __init__(self, value: T1 | E):
        ...

    def apply(self, f: Callable[[T1], "ResultType[T2, E]"]) -> "ResultType[T2, E]":  # type: ignore
        ...

    def fold(self, f: Callable[[T1, T2], "ResultType[T1, E]"], i: Iterable[T2]) -> "ResultType[T1, E]":  # type: ignore
        ...

    @classmethod
    def binds(cls, f: Callable[P, T1]) -> Callable[P, "ResultType[T1, E]"]:
        ...


def Result(ok: Type[T], er: Type[E]) -> Type[ResultType[T, E]]:
    class _Result(ResultType[T1, _E]):
        def __init__(self, value: T1 | _E):
            if isinstance(value, ok):
                self.value = Ok[T1](cast(T1, value))
            else:
                self.value = Er[_E](cast(_E, value))

        def apply(self, f: Callable[[T1], ResultType[T2, _E]]) -> ResultType[T2, _E]:
            match self.value:
                case Ok(v):
                    return f(v)
                case Er(e):
                    return _Result[T2, _E](e)

        def fold(
            self, f: Callable[[T1, T2], ResultType[T1, _E]], i: Iterable[T2]
        ) -> ResultType[T1, _E]:
            return reduce(lambda acc, x: acc.apply(lambda a: f(a, x)), i, self)

        def __call__(self, d: T1 | None = None) -> T1:
            match self.value:
                case Ok(v):
                    return v
                case Er(e):
                    if d is None:
                        raise e
                    return d

        def ok(self) -> bool:
            return isinstance(self.value, ok)

        @classmethod
        def binds(
            cls: Type["_Result[T1, _E]"], f: Callable[P, T1]
        ) -> Callable[P, "_Result[T1, _E]"]:
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> "_Result[T1, _E]":
                try:
                    return _Result[T1, _E](f(*args, **kwargs))
                except er as e:
                    return _Result[T1, _E](e)

            return inner

    return _Result[ok, er]
