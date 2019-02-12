import decimal
from functools import partial, reduce
from typing import Any, Dict, Hashable, List, TypeVar, Union

from .converters import Converter, Equiv, Filter, Range, Transform

T = TypeVar("T")

ALIASES: Dict[Any, Converter] = {
    # `str` filters
    **{
        func: Filter(func)
        for func in (
            getattr(str, attr) for attr in dir(str) if attr.startswith("is")
        )
    },
    # Special transforms
    bin: Transform(partial(int, base=2)),
    oct: Transform(partial(int, base=8)),
    decimal.Decimal: Transform(
        decimal.Decimal, raised_if_invalid=decimal.InvalidOperation
    ),
    # Equivalents
    bool: Equiv(
        {
            True: {"true", "True", "yes", "y", "1"},
            False: {"false", "False", "no", "n", "0"},
        }
    ),
    None: Equiv({None: {"null", "none"}}),
    # Other
    range: Range(),
}
"""Default aliases that are registered when using :func:`Brain.default <deduce.knowledge.Brain.default>`."""


class Brain:
    """A container for converter aliases. Truly a know-it-all."""

    def __init__(self):
        self._aliases: Dict[Any, Converter] = {}

    @classmethod
    def default(cls) -> "Brain":
        """Build and return the default brain.

        This brain knows about converter aliases defined in
        the ``aliases`` module.

        Returns
        -------
        brain : Brain
        """
        brain = cls()
        for alias, converter in ALIASES.items():
            brain.learn(alias, converter)
        return brain

    def learn(self, alias: Hashable, converter: Converter):
        """Learn about a new converter alias.

        Parameters
        ----------
        alias : hashable
        converter : Converter
        """
        self._aliases[alias] = converter

    def which(self, alias: T) -> Union[Converter, T]:
        """Retrieve which converter corresponds to an alias.

        Parameters
        ----------
        alias : hashable

        Returns
        -------
        converter : Converter or None
            This is `None` if no converter is known for `alias`.
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
