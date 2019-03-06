from functools import reduce, partial
from typing import Any, Dict, Hashable, List, Union, Callable

from .aliases import ALIASES
from .converters import Converter, Transform


_UNSPECIFIED = object()


class Registry:
    """A registry of converter aliases."""

    def __init__(self):
        self._aliases: Dict[Hashable, Converter] = {}

    @classmethod
    def default(cls) -> "Registry":
        """Build and return the default registry.

        This registry has convert aliases defined in the ``aliases`` module.

        Returns
        -------
        registry : Registry
        """
        registry = cls()
        for alias, converter in ALIASES.items():
            registry.converter(converter, alias=alias)
        return registry

    def converter(self, func: Callable = None, alias: Hashable = _UNSPECIFIED):
        """Add a new converter.

        This can be used as a decorator or as a regular function.

        Parameters
        ----------
        func : callable or ``Converter``
        alias : hashable (str, function, tuple, etc.), optional
            Defaults to the name of ``func``.
        """
        if func is None:
            return partial(self.converter, alias=alias)

        if alias is _UNSPECIFIED:
            alias = func.__name__

        self._aliases[alias] = func

        return func

    def get(self, alias: Hashable) -> Converter:
        """Retrieve the converter that corresponds to an alias.

        Parameters
        ----------
        alias : hashable (str, function, tuple, etc.)

        Returns
        -------
        converter : Converter
            This is the `alias` itself if no converter is
            registered for `alias`.
        """
        return self._aliases.get(alias, alias)

    def chain(
        self, *aliases_or_converters: Union[Hashable, Converter]
    ) -> Transform:
        """Chain converters into a single one.

        The input converters can also be given by alias.

        Parameters
        ----------
        *aliases_or_converters: alias or converter.

        Returns
        -------
        chained : Transform
        """
        converters: List[Converter] = [
            self.get(value) for value in aliases_or_converters
        ]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
