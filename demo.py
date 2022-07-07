from src.maybe import MH, MU, Just, Maybe, Nothing


def foo_or_bar(fbar: str) -> "Maybe[str]":
    if fbar in ("foo", "bar"):
        return Just(fbar)
    return Nothing()


@MU[str].bind
def binder(h: "MH[str]", s: str) -> "Maybe[str]":
    f1 = foo_or_bar(s)(h)
    return Just(f"{f1} and {s}")


def main():

    match foo_or_bar("foo"):
        case Just(v):
            print(f"{v}!")
        case Nothing():
            print("Aw shucks!")

    match binder("neither"):
        case Nothing():
            print("Expected that")
        case _:
            print("That's surprising!")


if __name__ == "__main__":
    main()
