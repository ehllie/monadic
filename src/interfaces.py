from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, Protocol, Type, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
U = TypeVar("U", bound="Unwrappable[Any]")
CO = TypeVar("CO", covariant=True)


class Monad(Protocol[T]):
    def __init__(self, value: T):
        ...

    # Can't define it as (M, Callable[[T], M]) -> M
    # Type checker claims that for the subclass of type S,
    # (S, Callable[[T], S]) -> S) is incomatible with the superclass
    # See https://github.com/python/mypy/issues/1317
    # Decided to be strict here and type ignore in child classes
    def apply(self, f: Callable[[T], "Monad[CO]"], /) -> "Monad[CO]":
        ...


class Foldable(Protocol[T1]):
    def fold(self, f: Callable[[T2], "Foldable[T1]"], l: list[T2]) -> "Foldable[T1]":
        ...


class Unwrappable(Protocol[T]):
    @classmethod
    def binds(cls: Type[U], f: Callable[P, T], /) -> Callable[P, U]:
        """Converts a funtion of type (*args, **kwargs) -> T, into a (*args, **kwargs) -> Unwrappable[T]"""
        ...

    def __call__(self, d: T | None = None, /) -> T:
        ...

    def unwrap(self, d: T | None = None, /) -> T:
        """Unwraps the value inside. Can throw an exception if no default value is provided"""
        ...

    def ok(self) -> bool:
        """Returns True if it's safe to unwrap"""
        ...


def bind(f: Callable[Concatenate[Callable[[U], Any], P], U], /) -> Callable[P, U]:
    class End(Exception):
        def __init__(self, value: U):
            self.value = value

    def handle(wrapped: U) -> Any:
        if wrapped.ok():
            return wrapped.unwrap()
        raise End(wrapped)

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> U:
        try:
            return f(handle, *args, **kwargs)
        except End as e:
            return e.value

    return inner
