from functools import reduce
from typing import Any, Dict, Hashable, List, Union, Optional

from .aliases import ALIASES
from .converters import Converter, Transform


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
            registry.add(alias, converter)
        return registry

    def add(self, alias: Hashable, converter: Converter):
        """Add a new converter alias.

        From then on, the registry will know which converter to use
        when seeing this alias.

        Parameters
        ----------
        alias : hashable (str, function, tuple, etc.)
        converter : Converter
        """
        self._aliases[alias] = converter

    def alias(self, alias: Hashable):
        """Add a new alias (decorator syntax).

        See Also
        --------
        add
        """

        def decorate(func):
            self.add(alias, func)
            return func

        return decorate

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

    def chain(self, *clues_or_converters: Union[Converter, Any]) -> Transform:
        """Chain converters into a single one.

        The input converters can also be given by clue.

        Parameters
        ----------
        *clues_or_converters: clue or converter.

        Returns
        -------
        chained : Transform
        """
        converters: List[Converter] = [
            self.get(value) for value in clues_or_converters
        ]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
