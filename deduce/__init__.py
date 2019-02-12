from .converters import *
from .knowledge import Brain
from .punctuate import punctuate, ConversionError

__version__ = "0.0.0"

_BRAIN = Brain.default()

# Pre-bound methods
# pylint: disable=invalid-name
learn = _BRAIN.learn
which = _BRAIN.which
chain = _BRAIN.chain
