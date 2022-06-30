from functools import wraps
from typing import Any, Callable, ParamSpec, Protocol, Type, TypeVar, cast

T = TypeVar("T")
T1 = TypeVar("T1")
P = ParamSpec("P")
R = TypeVar("R")
E = TypeVar("E", bound=Exception)
E1 = TypeVar("E1", bound=Exception)
U = TypeVar("U", bound="Unwrappable[Any]")


class Monad(Protocol[T]):
    def __init__(self, value: T):
        ...

    def apply(self, f: Callable[[T], R]) -> "Monad[R]":
        ...


class Unwrappable(Protocol[T]):
    @classmethod
    def binds(cls: Type[U], f: Callable[P, T]) -> Callable[P, U]:
        ...

    # @classmethod
    # def narrow(
    #     cls: Type[U], f: Callable[Concatenate[Any, P], Any]
    # ) -> Callable[P, U]:
    #     ...

    def __call__(self) -> T:
        ...

    def ok(self) -> bool:
        ...


class MaybeType(Monad[T], Unwrappable[T], Protocol[T]):
    def __init__(self, value: T | None):
        ...

    @classmethod
    def binds(cls, f: Callable[P, T | None]) -> Callable[P, "MaybeType[T]"]:
        ...

    # @classmethod
    # def narrow(
    #     cls, f: Callable[Concatenate[Type[R], P], "MaybeType[R]"]
    #     ) -> Callable[P, "MaybeType[T]"]:
    #     ...


class Nothing(Exception):
    pass


def Maybe(typ: Type[T1]) -> Type[MaybeType[T1]]:
    class _Maybe(MaybeType[T]):
        def __init__(self, value: T | None):
            self.value = value

        def apply(self, f: Callable[[T], R]) -> "_Maybe[R]":
            if self.value is None:
                return _Maybe[R](None)
            else:
                return _Maybe[R](f(self.value))

        def __call__(self) -> T:
            if self.value is None:
                raise Nothing()
            else:
                return self.value

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

        # @classmethod
        # def narrow(
        #     cls, f: Callable[Concatenate[Type[R], P], "_Maybe[R]"]
        # ) -> Callable[P, "_Maybe[T]"]:
        #     @wraps(f)
        #     def inner(*args: P.args, **kwargs: P.kwargs) -> "_Maybe[T]":
        #         return f(cls, *args, **kwargs)
        #     return inner

    return _Maybe[typ]


class ResultType(Monad[T], Unwrappable[T], Protocol[T, E]):
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
            self.value = value

        def apply(self, f: Callable[[T], R]) -> "_Result[R, E]":
            if isinstance(self.value, ok):
                ret = f(cast(T, self.value))
                return _Result[R, E](ret)
            else:
                return _Result[R, E](cast(E, self.value))

        def __call__(self) -> T:
            if isinstance(self.value, ok):
                return cast(T, self.value)
            raise cast(E, self.value)

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
