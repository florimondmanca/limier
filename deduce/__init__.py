from .converters import *
from .decorators import deduce
from .exceptions import ConversionError
from .clues import Detective

__version__ = "0.0.0"

_DETECTIVE = Detective.default()

# Pre-bound methods
# pylint: disable=invalid-name
record = _DETECTIVE.record
retrieve = _DETECTIVE.retrieve
chain = _DETECTIVE.chain
