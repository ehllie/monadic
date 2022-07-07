import pytest

from src.maybe import *


@Maybe[str].binds
def sometimes(ask: str) -> str | None:
    if ask == "do nothing":
        return None
    else:
        return ask


def foo_xor_bar(fbar1: str, fbar2: str) -> Maybe[str]:
    if fbar1 == fbar2 == "foo":
        return Just("foo")
    if fbar1 == fbar2 == "bar":
        return Just("bar")
    return Nothing()


def test_nothing():
    assert sometimes("do nothing") == Nothing()


def test_just():
    assert sometimes("do something") == Just("do something")


def test_not_just():
    assert sometimes("do something") != Just("do something else")


def test_not_just2():
    assert sometimes("do something") != Nothing()


def test_throws_nothing():
    pytest.raises(Nothing, lambda: sometimes("do nothing")())


def test_binds_nothing():
    @Maybe[str].binds
    def bind() -> str:
        s1 = sometimes("do something")()
        s2 = sometimes("do nothing")()
        return s1 + s2

    assert bind() == Nothing()


def test_binds_something():
    @Maybe[str].binds
    def bind() -> str:
        s1 = sometimes("do something")()
        s2 = sometimes("do something else")()
        return ", ".join((s1, s2))

    assert bind() == Just("do something, do something else")


def test_fold_empty():
    assert Just("foo").fold(foo_xor_bar, []) == Just("foo")


def test_fold_something():
    assert Just("foo").fold(foo_xor_bar, ["foo", "foo"]) == Just("foo")


def test_fold_nothing():
    assert Just("foo").fold(foo_xor_bar, ["foo", "bar"]) == Nothing()


def test_fold_nothing_2():
    assert Nothing().fold(foo_xor_bar, ["foo", "foo"]) == Nothing()


def test_apply():
    assert Just("foo").apply(Maybe[int].binds(len)) == Just(3)


def test_apply2():
    assert Nothing().apply(Maybe[int].binds(len)) == Nothing()
