import pytest

from src.interfaces import Handler, UnwrapError
from src.maybe import *


def sometimes(ask: str) -> "Maybe[str]":
    if ask == "do nothing":
        return Nothing()
    else:
        return Just(ask)


def foo_xor_bar(fbar1: str, fbar2: str) -> "Maybe[str]":
    if fbar1 == fbar2 == "foo":
        return Just("foo")
    if fbar1 == fbar2 == "bar":
        return Just("bar")
    return Nothing()


@MBinder[tuple[str, str, str]].bind
def ask_three(h: Handler, q1: str, q2: str, q3: str) -> "Maybe[tuple[str, str, str]]":
    r1 = sometimes(q1)(h)
    r2 = sometimes(q2)(h)
    r3 = sometimes(q3)(h)
    return Just((r1, r2, r3))


def test_nothing():
    assert sometimes("do nothing") == Nothing()


def test_just():
    assert sometimes("do something") == Just("do something")


def test_not_just():
    assert sometimes("do something") != Just("do something else")


def test_not_just2():
    assert sometimes("do something") != Nothing()


def test_unwrap_nothing():
    pytest.raises(UnwrapError, lambda: sometimes("do nothing").unwrap())


def test_unwrap_nothing_default():
    assert Nothing[int]().unwrap(4) == 4


def test_unwrap_just():
    assert Just("1").unwrap() == "1"


def test_unwrap_just_default():
    assert Just("1").unwrap("5") == "1"


def test_binds_nothing():

    assert ask_three("thing 1", "do nothing", "thing 2") == Nothing()


def test_binds_something():
    assert ask_three("thing 1", "thing 2", "thing 3") == Just(
        ("thing 1", "thing 2", "thing 3")
    )


def test_fold_empty():
    assert Just("foo").fold(foo_xor_bar, []) == Just("foo")


def test_fold_something():
    assert Just("foo").fold(foo_xor_bar, ["foo", "foo"]) == Just("foo")


def test_fold_nothing():
    assert Just("foo").fold(foo_xor_bar, ["foo", "bar"]) == Nothing()


def test_fold_nothing_2():
    assert Nothing().fold(foo_xor_bar, ["foo", "foo"]) == Nothing()


def test_apply():
    assert Just("foo").apply(lambda s: Just(len(s))) == Just(3)


def test_apply2():
    assert Nothing().apply(lambda s: Just(len(s))) == Nothing()
