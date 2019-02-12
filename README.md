# Colon

Colon is a conversion and validation toolkit powered by type annotations.

It is especially handy to automatically cast parameters passed to functions. A typical use case is processing route parameters in the context of web routing.

## Install

Colon is released to PyPI and can be installed using `pip`:

```bash
pip install colon
```

## Basic usage

```python
from colon import punctuate, chain

# Custom converter: validate that the input value is positive
def positive(value: int) -> int:
    if value < 0:
        raise ValueError("Expected positive value")
    return value

# Building custom converters is easy!
# Here, we chain two converters together.
positive_int = chain(int, positive)

# Punctuated function: converts inputs using the type annotation.
@punctuate
def compute(x: int, times: positive_int) -> float:
    return x * times

result = compute("2", times="2.5")
assert result == 5
```
