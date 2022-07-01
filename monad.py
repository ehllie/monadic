from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, ParamSpec, Protocol, Type, TypeVar, cast

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
P = ParamSpec("P")
R = TypeVar("R")
E = TypeVar("E", bound=Exception)
E1 = TypeVar("E1", bound=Exception)
U = TypeVar("U", bound="Unwrappable[Any]")


class Monad(Protocol[T]):
    def __init__(self, value: T):
        ...

    def apply(self, f: Callable[[T], R], /) -> "Monad[R]":
        ...


class Unwrappable(Protocol[T]):
    @classmethod
    def binds(cls: Type[U], f: Callable[P, T], /) -> Callable[P, U]:
        """Converts a funtion of type (*args, **kwargs) -> T, into a (*args, **kwargs) -> Unwrappable[T]"""
        ...

    # @classmethod
    # def narrow(
    #     cls: Type[U], f: Callable[Concatenate[Any, P], Any]
    # ) -> Callable[P, U]:
    #     ...

    def __call__(self, d: T | None = None, /) -> T:
        """Unwraps the value inside. Can throw an exception if no default value is provided"""
        ...

    def ok(self) -> bool:
        ...


class MaybeMeta(Monad[T], Unwrappable[T], Protocol[T]):
    def __init__(self, value: T | None):
        ...

    @classmethod
    def binds(cls, f: Callable[P, T | None], /) -> Callable[P, "MaybeMeta[T]"]:
        ...

    # @classmethod
    # def narrow(
    #     cls, f: Callable[Concatenate[Type[R], P], "MaybeType[R]"]
    #     ) -> Callable[P, "MaybeType[T]"]:
    #     ...


class Nothing(MaybeMeta[None], Protocol):
    def __init__(self):
        ...

    def __call__(self, d: T | None = None, /) -> T:  # type: ignore
        ...


@dataclass
class Just(MaybeMeta[T], Protocol[T]):
    def __init__(self, value: T):
        ...

    value: T

J = TypeVar("J", bound="Just[Any]")

class MaybeType(MaybeMeta[T], Protocol[T]):
    def __new__(cls, value: T | None) -> Just[T] | Nothing:
        ...

    def __call__(self, d: T | None = None, /) -> Just[T] | Nothing:
        ...


def Maybe(typ: Type[T1]) -> Type[MaybeType[T1]]:
    class _Just(Just[T]):
        def __init__(self, value: T):
            self.value = value

        def apply(self, f: Callable[[T], R], /) -> "_Just[R]":
            return _Just(f(self.value))

        def __call__(self, _: T | None = None) -> T:
            return self.value

        def ok(self) -> bool:
            return True

        @classmethod
        def binds(cls, _) -> Any:
            ...

    class _Nothing(Nothing, Exception):
        def __init__(self):
            pass

        def apply(self, _: Callable[..., Any]) -> "MaybeMeta[Any]":
            return self

        def __call__(self, d: T | None = None) -> T:
            if d is None:
                raise self
            return d

        def ok(self) -> bool:
            return False

        @classmethod
        def binds(cls, _) -> Any:
            ...

    class _Maybe(MaybeType[T]):
        def __new__(cls, value: T | None) -> _Just[T] | _Nothing:
            return _Just(value) if value is not None else _Nothing()

        def apply(self, _: Callable[[T], R], /) -> "_Maybe[R]":
            ...

        def __call__(self, _: T | None = None) -> T:
            ...

        def ok(self) -> bool:
            ...

        @classmethod
        def binds(cls, f: Callable[P, T | None]) -> Callable[P, "_Maybe[T]"]:
            @wraps(f)
            def inner(*args: P.args, **kwargs: P.kwargs) -> "_Maybe[T]":
                try:
                    return _Maybe[T](f(*args, **kwargs))
                except _Nothing:
                    return _Maybe[T](None)

            return inner

        # @classmethod
        # def narrow(
        #     cls, f: Callable[Concatenate[Type[R], P], "_Maybe[R]"]
        # ) -> Callable[P, "_Maybe[T]"]:
        #     @wraps(f)
        #     def inner(*args: P.args, **kwargs: P.kwargs) -> "_Maybe[T]":
        #         return f(cls, *args, **kwargs)
        #     return inner

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

    def apply(self, f: Callable[[T], R]) -> "ResultType[R, E]":
        ...

    @classmethod
    def binds(cls, f: Callable[P, T]) -> Callable[P, "ResultType[T, E]"]:
        ...


def Result(ok: Type[T1], er: Type[E1]) -> Type[ResultType[T1, E1]]:
    class _Result(ResultType[T, E]):
        def __init__(self, value: T | E):
            if isinstance(value, ok):
                self.value = Ok[T](v=cast(T, value))
            else:
                self.value = Er[E](e=cast(E, value))

        def apply(self, f: Callable[[T], R]) -> "_Result[R, E]":
            match self.value:
                case Ok(v):
                    return _Result[R, E](f(v))
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
