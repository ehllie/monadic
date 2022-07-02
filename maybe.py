from dataclasses import dataclass
from functools import reduce, wraps
from typing import Callable, Generic, Iterable, ParamSpec, Protocol, Type, TypeVar, cast

from interfaces import Foldable, Monad, Unwrappable

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
CO = TypeVar("CO", covariant=True)


class Nothing(Exception):
    pass


@dataclass
class Just(Generic[T]):
    v: T


class MaybeType(Monad[T1], Unwrappable[T1], Foldable[T1], Protocol[T1]):
    value: Just[T1] | Nothing

    def __init__(self, value: T1 | None):
        ...

    def apply(self, f: Callable[[T1], "MaybeType[CO]"]) -> "MaybeType[CO]":  # type: ignore
        ...

    def fold(self, f: Callable[[T1, T2], "MaybeType[T1]"], i: Iterable[T2]) -> "MaybeType[T1]":  # type: ignore
        ...

    @classmethod
    def binds(cls, f: Callable[P, T1 | None]) -> Callable[P, "MaybeType[T1]"]:
        ...


def Maybe(typ: Type[T]) -> Type[MaybeType[T]]:
    class _Maybe(MaybeType[T1]):
        def __init__(self, value: T1 | None):
            if isinstance(value, typ):
                self.value = Just[T1](cast(T1, value))
            else:
                self.value = Nothing()

        def apply(self, f: Callable[[T1], MaybeType[CO]]) -> MaybeType[CO]:
            match self.value:
                case Nothing():
                    return _Maybe[CO](None)
                case Just(v):
                    return f(v)

        def fold(
            self, f: Callable[[T1, T2], MaybeType[T1]], i: Iterable[T2]
        ) -> MaybeType[T1]:
            return reduce(lambda acc, x: acc.apply(lambda a: f(a, x)), i, self)

        def __call__(self, d: T1 | None = None) -> T1:
            match self.value:
                case Nothing():
                    if d is None:
                        raise self.value
                    return d
                case Just(v):
                    return v

        def ok(self) -> bool:
            return self.value is not None

        @classmethod
        def binds(cls, f: Callable[P, T1 | None]) -> Callable[P, "_Maybe[T1]"]:
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> "_Maybe[T1]":
                try:
                    return _Maybe[T1](f(*args, **kwargs))
                except Nothing:
                    return _Maybe[T1](None)

            return inner

    return _Maybe[typ]
