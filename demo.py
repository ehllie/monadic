from typing import Callable, TypeAlias, TypeVar

from src.interfaces import bind
from src.maybe import Just, Nothing

T = TypeVar("T")

MyBe: TypeAlias = Just[T] | Nothing

MBU: TypeAlias = Callable[["MyBe[T]"], T]


def foo_or_bar(fbar: str) -> "MyBe[str]":
    if fbar in ("foo", "bar"):
        return Just(fbar)
    return Nothing()


@bind
def binder(u: "MBU[str]", s: str) -> MyBe[str]:
    f1 = u(foo_or_bar(s))
    return Just(f"{f1} and {s}")


def main():

    match foo_or_bar("foo"):
        case Just(v):
            print(f"{v}!")
        case Nothing():
            print("Aw shucks!")

    print(binder("foo")("bar"))


if __name__ == "__main__":
    main()
