from methods import fold
from monad import Callable, Er, Ok, Result, ResultType

StrDict = Result(str, KeyError)


@StrDict.binds
def format_with(format: str, d: dict[str, str], keys: list[str]) -> str:
    vals = [d[k] for k in keys]
    return format.format(*vals)


def main():
    f_string = "I like, {0} and {1}!"
    my_dict = {"color": "purple", "language": "Haskell", "city": "Warsaw"}
    strings = [
        format_with(f_string, my_dict, ["city", "color"]),
        format_with(f_string, my_dict, ["language", "city"]),
        format_with(f_string, my_dict, ["color", "language"]),
        format_with(f_string, my_dict, ["name", "food"]),
    ]
    for s in strings:
        match s.value:
            case Ok(v):
                print(v)
            case Er(e):
                print("No such key:", e)

    get_key: Callable[
        [dict[str, str], str], ResultType[dict[str, str], KeyError]
    ] = Result(dict, KeyError).binds(lambda d, k: {**d, k: my_dict[k]})

    collect: Callable[
        [list[str]], ResultType[dict[str, str], KeyError]
        ] = lambda keys: fold(get_key, Result(dict, KeyError)({}), keys) # type: ignore

    collected = [
            collect(["city", "color"]),
            collect(["language", "city"]),
            collect(["color", "language", "city", "food"]),
            collect(["name", "food"]),
            ]
    for c in collected:
        match c.value:
            case Ok(v):
                print(v)
            case Er(e):
                print("No such key:", e)


if __name__ == "__main__":
    main()
