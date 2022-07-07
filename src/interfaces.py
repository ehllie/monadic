from abc import ABC, abstractmethod
from functools import wraps
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
    cast,
)

P = ParamSpec("P")
T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
U1 = TypeVar("U1", bound="Unwrappable[Any]")
U2 = TypeVar("U2", bound="Unwrappable[Any]")
U3 = TypeVar("U3", bound="Unwrappable[Any]")


class Monad(ABC):
    # Can't define it as (M, Callable[[T], M]) -> M
    # Type checker claims that for the subclass of type S,
    # (S, Callable[[T], S]) -> S) is incomatible with the superclass
    # See https://github.com/python/mypy/issues/1317
    @abstractmethod
    def apply(self, f: Callable[..., Any], /) -> "Monad":
        ...


class Foldable(ABC):
    @abstractmethod
    def fold(self, f: Callable[[Any, T], Any], l: list[T]) -> "Foldable":
        ...


class UnwrapError(Exception):
    pass


class Unwrappable(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, handle: Callable[[U1], T], /) -> T:
        ...

    @abstractmethod
    def unwrap(self, d: T | None = None, /) -> T:
        """Unwraps the value inside. Can throw an exception if no default value is provided"""
        ...

    @abstractmethod
    def ok(self) -> bool:
        """Returns True if it's safe to unwrap"""
        ...


Handler: TypeAlias = Callable[[Unwrappable[Any]], Any]


class Binder(Generic[U1]):
    @classmethod
    def bind(cls, f: Callable[Concatenate[Handler, P], U2], /) -> Callable[P, U1 | U2]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> U1 | U2:
            class End(Exception):
                def __init__(self, value: U2):
                    self.value = value

            def handle(uw: Unwrappable[Any]) -> Any:
                if uw.ok():
                    return uw.unwrap()
                else:
                    raise End(cast(U2, uw))

            try:
                return f(handle, *args, **kwargs)
            except End as e:
                return e.value

        return inner
