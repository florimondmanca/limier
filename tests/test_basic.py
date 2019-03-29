import pytest
from limier import converted, ConversionError


@converted
def add(x: int, y: int = 0) -> int:
    return x + y


@pytest.mark.parametrize(
    "args, kwargs, output",
    [
        [(1,), {}, 1],
        [(1, 2), {}, 3],
        [(), {"x": 1}, 1],
        [(), {"x": 2, "y": 3}, 5],
    ],
)
@pytest.mark.parametrize("typ", (int, float, str))
def test_basic(args, kwargs, output, typ):
    args = [typ(val) for val in args]
    kwargs = {key: typ(val) for key, val in kwargs.items()}
    assert add(*args, **kwargs) == output


@pytest.mark.parametrize("x, y", [("0.1", 1), ("foo", 2), (1, "foo")])
def test_conversion_errors(x, y):
    with pytest.raises(ConversionError):
        add(x, y)
