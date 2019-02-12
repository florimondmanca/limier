# Limier

Limier is a smart Python conversion and validation toolkit powered by type annotations.

It is especially handy to automatically cast parameters passed to functions. A typical use case is processing route parameters in the context of web routing.

## Install

Limier is released to PyPI and can be installed using `pip`:

```bash
pip install limier
```

## Basic usage

```python
from limier import deduce, chain

# Custom converter: validate that the input value is positive
def positive(value: int) -> int:
    if value < 0:
        raise ValueError("Expected positive value")
    return value

@deduce
def compute(x: int, times: chain(int, positive)) -> float:
    return x * times

result = compute("2", times="2.5")
assert result == 5
```
