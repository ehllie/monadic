from typing import Iterable, Type

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

    @DictResult.binds
    def add_k_v(d: dict[str, str], k: str) -> dict[str, str]:
        return {**d, k: my_dict[k]}

    empty = DictResult({})
    collected = (
        empty.fold(add_k_v, ("city", "color")),
        empty.fold(add_k_v, ("language", "city")),
        empty.fold(add_k_v, ("color", "language", "city", "food")),
        empty.fold(add_k_v, ("name", "food")),
    )
    for c in collected:
        match c.value:
            case Ok(v):
                print(v)
            case Er(e):
                print("No such key:", e)


if __name__ == "__main__":
    main()
