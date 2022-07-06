from typing import TypeAlias, TypeVar

from src.maybe import Just, Nothing

T = TypeVar("T")

MyBe: TypeAlias = Just[T] | Nothing


def main():
    def foo_or_bar(fbar: str) -> "MyBe[str]":
        if fbar in ("foo", "bar"):
            return Just(fbar)
        return Nothing()

    match foo_or_bar("foo"):
        case Just(v):
            print(f"{v}!")
        case Nothing():
            print("Aw shucks!")


if __name__ == "__main__":
    main()
