from .converters import *
from .decorators import converted
from .exceptions import ConversionError
from .registry import Registry

__version__ = "0.0.2"

_REGISTRY = Registry.default()

# Pre-bound methods
# pylint: disable=invalid-name
converter = _REGISTRY.converter
get = _REGISTRY.get
chain = _REGISTRY.chain
