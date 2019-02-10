import pytest
from colon import punctuate


def test_basic():
    def add(x: int, y: int = 0) -> int:
        return x + y

    add = punctuate(add)

    assert add(1, 2) == 3
    assert add("1", "2") == 3

    with pytest.raises(ValueError):
        add("0.1", 2)

    with pytest.raises(ValueError):
        add("foo", 2)
