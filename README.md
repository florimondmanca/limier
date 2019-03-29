# Limier

Limier is a smart toolkit for conversion and validation of function arguments in Python powered by type annotations.

A typical use case is the conversion of route parameters in the context of web routing.

## Install

```bash
pip install limier
```

## Basic usage

```python
from limier import converted, chain

# Custom converter: validate that the input value is positive
def positive(value: int) -> int:
    if value < 0:
        raise ValueError("Expected positive value")
    return value

@converted
def compute(x: int, times: chain(int, positive)) -> float:
    return x * times

result = compute("2", times="2.5")
assert result == 5
```
