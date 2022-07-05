from functools import partial
from typing import Iterable, Type, TypeVar

T1 = TypeVar("T1")
T2 = TypeVar("T2")

from result import Er, Ok, Result, ResultType

StrDict = Result(str, KeyError)


@StrDict.binds
def format_with(format: str, d: dict[str, str], keys: Iterable[str]) -> str:
    vals = (d[k] for k in keys)
    return format.format(*vals)


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
        match s.value:
            case Ok(v):
                print(v)
            case Er(e):
                print("No such key:", e)

    DictResult: Type[ResultType[dict[str, str], KeyError]] = Result(dict, KeyError)

    def add_k_v(source: dict[T1, T2], d: dict[T1, T2], k: T1) -> dict[T1, T2]:
        return {**d, k: source[k]}

    add_from_my = DictResult.binds(partial(add_k_v, my_dict))

    empty = DictResult({})
    collected = (
        empty.fold(add_from_my, ("city", "color")),
        empty.fold(add_from_my, ("language", "city")),
        empty.fold(add_from_my, ("color", "language", "city", "food")),
        empty.fold(add_from_my, ("name", "food")),
    )
    for c in collected:
        match c.value:
            case Ok(v):
                print(v)
            case Er(e):
                print("No such key:", e)


if __name__ == "__main__":
    main()
