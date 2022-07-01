from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, ParamSpec, Protocol, Type, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
T1 = TypeVar("T1")
E = TypeVar("E", bound=Exception)
E1 = TypeVar("E1", bound=Exception)
M = TypeVar("M", bound="Monad[Any]")
U = TypeVar("U", bound="Unwrappable[Any]")
RM = TypeVar("RM", bound="ResultType[Any, Any]")


class Monad(Protocol[T]):
    def __init__(self, value: T):
        ...

    # Can't define it as (M, Callable[[T], M]) -> M
    # Type checker claims that for the subclass of type S,
    # (S, Callable[[T], S]) -> S) is incomatible with the superclass
    # See https://github.com/python/mypy/issues/1317
    def apply(self: M, f: Callable[[T], Any]) -> M:
        ...


class Unwrappable(Protocol[T]):
    @classmethod
    def binds(cls: Type[U], f: Callable[P, T]) -> Callable[P, U]:
        """Converts a funtion of type (*args, **kwargs) -> T, into a (*args, **kwargs) -> Unwrappable[T]"""
        ...

    def __call__(self, d: T | None = None) -> T:
        """Unwraps the value inside. Can throw an exception if no default value is provided"""
        ...

    def ok(self) -> bool:
        """Returns True if it's safe to unwrap"""
        ...


class Nothing(Exception):
    pass


@dataclass
class Just(Generic[T]):
    v: T


class MaybeType(Monad[T], Unwrappable[T], Protocol[T]):
    value: Just[T] | Nothing

    def __init__(self, value: T | None):
        ...

    @classmethod
    def binds(cls, f: Callable[P, T | None]) -> Callable[P, "MaybeType[T]"]:
        ...


def Maybe(typ: Type[T1]) -> Type[MaybeType[T1]]:
    class _Maybe(MaybeType[T]):
        def __init__(self, value: T | None):
            if isinstance(value, typ):
                self.value = Just[T](cast(T, value))
            else:
                self.value = Nothing()

        def apply(self, f: Callable[[T], "_Maybe[R]"]) -> "_Maybe[R]":
            match self.value:
                case Nothing():
                    return _Maybe[R](None)
                case Just(v):
                    return f(v)

        def __call__(self, d: T | None = None) -> T:
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
        def binds(cls, f: Callable[P, T | None]) -> Callable[P, "_Maybe[T]"]:
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> "_Maybe[T]":
                try:
                    return _Maybe[T](f(*args, **kwargs))
                except Nothing:
                    return _Maybe[T](None)

            return inner

    return _Maybe[typ]


@dataclass
class Ok(Generic[T]):
    v: T


@dataclass
class Er(Generic[E]):
    e: E


class ResultType(Monad[T], Unwrappable[T], Protocol[T, E]):
    value: Ok[T] | Er[E]

    def __init__(self, value: T | E):
        ...

    def apply(self: RM, f: Callable[[T], Any]) -> RM:
        ...

    @classmethod
    def binds(cls, f: Callable[P, T]) -> Callable[P, "ResultType[T, E]"]:
        ...


def Result(ok: Type[T1], er: Type[E1]) -> Type[ResultType[T1, E1]]:
    class _Result(ResultType[T, E]):
        def __init__(self, value: T | E):
            if isinstance(value, ok):
                self.value = Ok[T](cast(T, value))
            else:
                self.value = Er[E](cast(E, value))

        def apply(self, f: Callable[[T], "_Result[R, E]"]) -> "_Result[R, E]":
            match self.value:
                case Ok(v):
                    return f(v)
                case Er(e):
                    return _Result[R, E](e)

        def __call__(self, d: T | None = None) -> T:
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
            cls: Type["_Result[T, E]"], f: Callable[P, T]
        ) -> Callable[P, "_Result[T, E]"]:
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> "_Result[T, E]":
                try:
                    return _Result[T, E](f(*args, **kwargs))
                except er as e:
                    return _Result[T, E](e)

            return inner

    return _Result[ok, er]
