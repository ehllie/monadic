from monad import Er, Ok, Result

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


if __name__ == "__main__":
    main()
