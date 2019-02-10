from .registry import Registry

__version__ = "0.0.0"

_REGISTRY = Registry.from_defaults()

# pylint: disable=invalid-name
register = _REGISTRY.register
get = _REGISTRY.get
chain = _REGISTRY.chain
