from functools import wraps
from inspect import Parameter, signature
from typing import Callable, Mapping

from .converters import Converter
from .registry import Registry
from .typevars import V
from .exceptions import ConversionError


def deduce(
    func: Callable[..., V], registry: Registry = None
) -> Callable[..., V]:
    """Build a deduced version of a function.

    Parameters
    ----------
    func : callable
    registry : Registry, optional
        A ``Registry`` object which has aliases to available converters.
        Defaults to ``Registry.default``.

    Returns
    -------
    deduced : callable
        Wrapper of ``func`` that applies converters to parameters
        that have a type annotation.
    """
    sig = signature(func)
    if registry is None:
        registry = Registry.default()

    converters: Mapping[str, Converter] = {
        name: registry.get(param.annotation) or param.annotation
        for name, param in sig.parameters.items()
        if param.annotation is not Parameter.empty
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        errors = {}

        for name, converter in converters.items():
            try:
                bound.arguments[name] = converter(bound.arguments[name])
            except ValueError as exc:
                errors[name] = str(exc)

        if errors:
            raise ConversionError(**errors)

        return func(*bound.args, **bound.kwargs)

    return wrapper
