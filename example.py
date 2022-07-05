from functools import partial
from typing import Iterable, TypeVar

T1 = TypeVar("T1")
T2 = TypeVar("T2")

from maybe import Just, Maybe, Nothing
from result import Err, Ok, Result


@Result[str, KeyError].capture(KeyError)
def format_with(format: str, d: dict[str, str], keys: Iterable[str]) -> str:
    vals = (d[k] for k in keys)
    return format.format(*vals)


@Maybe[str].binds
def sometimes(ask: str) -> str | None:
    if ask == "do nothing":
        return None
    else:
        return ask


def main():
    f_string = "I like, {} and {}!"
    my_dict = {"color": "purple", "language": "Haskell", "city": "Warsaw"}
    strings = (
        format_with(f_string, my_dict, ("city", "color")),
        format_with(f_string, my_dict, ("language", "city")),
        format_with(f_string, my_dict, ("color", "language")),
        format_with(f_string, my_dict, ("name", "food")),
    )
    for s in strings:
        match s.inst():
            case Ok(v):
                print(v)
            case Err(e):
                print("No such key:", e)

    def add_k_v(source: dict[T1, T2], d: dict[T1, T2], k: T1) -> dict[T1, T2]:
        return {**d, k: source[k]}

    add_from_my = Result[dict[str, str], KeyError].capture(KeyError)(
        partial(add_k_v, my_dict)
    )

    empty = Ok[dict[str, str], KeyError]({})
    collected = (
        empty.fold(add_from_my, ("city", "color")),
        empty.fold(add_from_my, ("language", "city")),
        empty.fold(add_from_my, ("color", "language", "city", "food")),
        empty.fold(add_from_my, ("name", "food")),
    )
    for c in collected:
        match c.inst():
            case Ok(v):
                print(v)
            case Err(e):
                print("No such key:", e)

    asks = ("do nothing", "do something")
    for ask in asks:
        match sometimes(ask).inst():
            case Just(v):
                print(v)
            case Nothing():
                print("Nothing")


if __name__ == "__main__":
    main()
