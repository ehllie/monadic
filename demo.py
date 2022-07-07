from src.interfaces import Handler
from src.maybe import Just, Maybe, MBinder, Nothing, TypeVar

T = TypeVar("T")


def foo_or_bar(fbar: str) -> "Maybe[str]":
    if fbar in ("foo", "bar"):
        return Just(fbar)
    return Nothing()


@MBinder[str].bind
def binds(h: Handler, s: str) -> "Maybe[str]":
    f1 = foo_or_bar(s)(h)
    return Just(f"{f1} and {s}")


def main():

    match foo_or_bar("foo"):
        case Just(v):
            print(f"{v}!")
        case Nothing():
            print("Aw shucks!")

    match binds("neither"):
        case Nothing():
            print("Expected that")
        case _:
            print("That's surprising!")


if __name__ == "__main__":
    main()
