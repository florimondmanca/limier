from functools import reduce
from typing import Any, Dict, Hashable, List, Union, TypeVar

from .aliases import ALIASES
from .converters import Converter, Transform

T = TypeVar("T")


class Registry:
    """A registry of converter aliases."""

    def __init__(self):
        self._aliases: Dict[Any, Converter] = {}

    @classmethod
    def default(cls) -> "Registry":
        """Build and return the default registry.

        The registry will contain aliases defined in the ``aliases`` module.

        Returns
        -------
        registry : Registry
        """
        registry = cls()
        for alias, converter in ALIASES.items():
            registry.alias(alias, converter)
        return registry

    def alias(self, alias: Hashable, converter: Converter):
        """Register a new converter alias.

        Parameters
        ----------
        alias : hashable
        converter : Converter
        """
        self._aliases[alias] = converter

    def get(self, alias: T) -> Union[Converter, T]:
        """Retrieve a converter by alias.

        Parameters
        ----------
        alias : hashable

        Returns
        -------
        converter : Converter or None
            This is `None` if no converter is registered for `alias`.
        """
        return self._aliases.get(alias, alias)

    def chain(self, *args: Union[Converter, Any]) -> Transform:
        """Build a chain converter from multiple converters.

        The input converters can also be given by alias.

        Parameters
        ----------
        *args: converter or alias

        Returns
        -------
        chained : Transform
        """
        converters: List[Converter] = [self.get(arg) for arg in args]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
