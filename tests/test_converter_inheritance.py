import collections
from typing import Hashable, Iterable, Reversible

import pytest
from attrs import define

from cattrs import BaseConverter


def test_inheritance(converter):
    @define
    class A:
        i: int

    @define
    class B(A):
        j: int

    assert A(1) == converter.structure({"i": 1}, A)
    assert B(1, 2) == converter.structure({"i": 1, "j": 2}, B)


def test_gen_hook_priority(converter: BaseConverter):
    """Autogenerated hooks should not take priority over manual hooks."""

    @define
    class A:
        i: int

    @define
    class B(A):
        pass

    # This will generate a hook.
    assert converter.structure({"i": 1}, B) == B(1)

    # Now we register a manual hook for the superclass.
    converter.register_structure_hook(A, lambda o, t: t(o["i"] + 1))

    # This should still work, but using the new hook instead.
    assert converter.structure({"i": 1}, B) == B(2)


@pytest.mark.parametrize("typing_cls", [Hashable, Iterable, Reversible, Iterable[int]])
def test_inherit_typing(converter: BaseConverter, typing_cls):
    """Stuff from typing.* resolves to runtime to collections.abc.*.

    Hence, typing.* are of a special alias type which we want to check if
    cattrs handles them correctly.
    """

    @define
    class A(typing_cls):  # pragma: nocover
        i: int = 0

        def __hash__(self):
            return hash(self.i)

        def __iter__(self):
            return iter([self.i])

        def __reversed__(self):
            return iter([self.i])

    assert converter.structure({"i": 1}, A) == A(i=1)


@pytest.mark.parametrize(
    "collections_abc_cls",
    [
        collections.abc.Hashable,
        collections.abc.Iterable,
        collections.abc.Reversible,
        collections.abc.Iterable[int],
    ],
)
def test_inherit_collections_abc(converter: BaseConverter, collections_abc_cls):
    """As extension of test_inherit_typing, check if collections.abc.* work."""

    @define
    class A(collections_abc_cls):  # pragma: nocover
        i: int = 0

        def __hash__(self):
            return hash(self.i)

        def __iter__(self):
            return iter([self.i])

        def __reversed__(self):
            return iter([self.i])

    assert converter.structure({"i": 1}, A) == A(i=1)
