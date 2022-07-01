from functools import reduce
from typing import Callable, Iterable, TypeVar

from monad import Monad

T1 = TypeVar("T1")
T2 = TypeVar("T2")


def fold(
    func: Callable[[T1, T2], Monad[T1]], seed: Monad[T1], iter: Iterable[T2]
) -> Monad[T1]:
    return reduce(lambda acc, x: acc.apply(lambda a: func(a, x)), iter, seed)
