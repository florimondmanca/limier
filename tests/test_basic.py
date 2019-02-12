import pytest
from deduce import punctuate, ConversionError


def test_basic():
    @punctuate
    def add(x: int, y: int = 0) -> int:
        return x + y

    assert add(1, 2) == 3
    assert add("1", "2") == 3

    with pytest.raises(ConversionError):
        add("0.1", 2)

    with pytest.raises(ConversionError):
        add("foo", 2)
