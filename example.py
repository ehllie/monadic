from typing import TypeAlias

from .monad import Just, Maybe, Nothing

MaybeInt: TypeAlias = Maybe(int)


def div(a: int, b: int) -> Just[int] | Nothing:
    if b == 0:
        return MaybeInt(None)
    return MaybeInt(a // b)

def main():
    match div(10, 2):
        case Nothing():
            print("Division by zero")
        case Just(x):
            print(f"10 / 2 = {x}")
    

if __name__ == "__main__":
    main()
