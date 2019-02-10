from functools import reduce
from typing import Any, Callable, Dict, Hashable, List, Union

from .aliases import ALIASES
from .converters import Converter, Transform
from .typevars import T, V


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
            registry.register(alias, converter)
        return registry

    def register(self, alias: Hashable, converter: Converter):
        """Register a new alias.

        Parameters
        ----------
        alias : hashable
        converter : Converter
        """
        self._aliases[alias] = converter

    def get(self, annotation: Union[Callable[[T], V], Any]) -> Converter[T, V]:
        """Retrieve a converter.

        If no converter is aliased from `annotation`, the annotation itself is
        used to build a ``Transform`` converter.

        Parameters
        ----------
        annotation : callable or alias

        Returns
        -------
        converter : Converter
        """
        try:
            return self._aliases[annotation]
        except KeyError:
            return Transform(annotation)

    def chain(self, *args: Union[Converter, Any]) -> Converter:
        """Build a chain converter from multiple converters.

        The input converters can also be given by alias.

        Parameters
        ----------
        *args: converter or any

        Returns
        -------
        chained : Converter
        """

        converters: List[Converter] = [self.get(arg) for arg in args]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
