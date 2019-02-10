from collections import OrderedDict, defaultdict
from functools import wraps
from inspect import Parameter, signature
from itertools import zip_longest
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from .converters import Converter
from .registry import Registry
from .typevars import V

__version__ = "0.0.0"

_REGISTRY = Registry.default()

# Pre-bound methods
# pylint: disable=invalid-name
register = _REGISTRY.register
get = _REGISTRY.get
chain = _REGISTRY.chain


def _filter(
    parameters: Mapping[str, Parameter], required: bool
) -> Dict[str, Parameter]:
    # NOTE: `parameters` is an `OrderedDict` and so is this filtered dict,
    # which ensures that the order of parameters declared on `func` is kept
    # intact.
    return OrderedDict(
        {
            name: param
            for name, param in parameters.items()
            if (required and param.default is Parameter.empty)
            or (not required and param.default is not Parameter.empty)
        }
    )


def punctuate(
    func: Callable[..., V], registry: Optional[Registry] = None
) -> Callable[..., V]:
    """Return a punctuated version of a function.

    Parameters
    ----------
    func : callable
    registry : Registry, optional
        A `Registry` object. Defaults to the default registry.

    Returns
    -------
    punctuated : callable
        Wrapper of `func` that applies converters to arguments and
        keyword arguments that have a type annotation.
    """

    _registry = registry if registry is not None else _REGISTRY

    # Build cache of converters
    sig = signature(func)
    params = sig.parameters

    args_converters: List[Converter] = []
    kwargs_converters: Dict[str, Converter] = defaultdict(
        # Default to `identity` so that given kwargs that are not expected
        # by `func` are passed unchanged to `func` for failure.
        lambda: Converter.identity
    )

    for param in _filter(params, required=True).values():
        if param.annotation is not Parameter.empty:
            args_converters.append(_registry.get(param.annotation))
        else:
            args_converters.append(Converter.identity)

    for name, param in _filter(params, required=False).items():
        if param.annotation is not Parameter.empty:
            kwargs_converters[name] = _registry.get(param.annotation)

    def punctuated_args(args: Tuple) -> Tuple:
        return tuple(
            converter(value)
            # Use `zip_longest` with `identity` as a fill value so that
            # superfluous positional arguments are passed unchanged to
            # `func` for failure.
            for converter, value in zip_longest(
                args_converters, args, fillvalue=Converter.identity
            )
            # This may be the case if `len(args) < len(args_converters)`
            # (not enough positional arguments were given).
            if value is not Converter.identity
        )

    def puncuated_kwargs(kwargs: Dict) -> Dict:
        return {
            name: kwargs_converters[name](value)
            for name, value in kwargs.items()
        }

    @wraps(func)
    def punctuated(*args: Any, **kwargs: Any) -> V:
        return func(*punctuated_args(*args), **puncuated_kwargs(kwargs))

    return punctuated
