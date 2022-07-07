from functools import wraps
from typing import Any, Callable, Concatenate, Generic, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U", bound="Unwrappable[Any]")


class Monad(Protocol):
    def __init__(self):
        ...

    # Can't define it as (M, Callable[[T], M]) -> M
    # Type checker claims that for the subclass of type S,
    # (S, Callable[[T], S]) -> S) is incomatible with the superclass
    # See https://github.com/python/mypy/issues/1317
    def apply(self, f: Callable[..., Any], /) -> "Monad":
        ...


class Foldable(Protocol):
    def fold(self, f: Callable[[Any, T], Any], l: list[T]) -> "Foldable":
        ...


class UnwrapError(Exception):
    pass


class Unwrappable(Protocol[T]):
    def __call__(self, handle: Callable[[U], T], /) -> T:
        ...

    def unwrap(self, d: T | None = None, /) -> T:
        """Unwraps the value inside. Can throw an exception if no default value is provided"""
        ...

    def ok(self) -> bool:
        """Returns True if it's safe to unwrap"""
        ...


class UW(Generic[U, T]):
    @classmethod
    def bind(
        cls, f: Callable[Concatenate[Callable[[U], T], P], U], /
    ) -> Callable[P, U]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> U:
            class End(Exception):
                def __init__(self, value: U):
                    self.value = value

            def handle(uw: U) -> T:
                if uw.ok():
                    return uw.unwrap()
                else:
                    raise End(uw)

            try:
                return f(handle, *args, **kwargs)
            except End as e:
                return e.value

        return inner
