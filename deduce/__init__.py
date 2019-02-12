from .converters import *
from .registry import Registry
from .punctuate import punctuate, ConversionError

__version__ = "0.0.0"

_REGISTRY = Registry.default()

# Pre-bound methods
# pylint: disable=invalid-name
alias = _REGISTRY.alias
get = _REGISTRY.get
chain = _REGISTRY.chain
