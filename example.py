from .monad import Result

StrDict = Result(str, KeyError)


@StrDict.binds
def format_with(format: str, d: dict[str, str], keys: list[str]) -> str:
    vals = [d[k] for k in keys]
    return format.format(*vals)

