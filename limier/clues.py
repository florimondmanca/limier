import decimal
from functools import partial, reduce
from typing import Any, Dict, Hashable, List, TypeVar, Union

from .converters import Converter, Equiv, Filter, Range, Transform

T = TypeVar("T")

CLUES: Dict[Any, Converter] = {
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
"""Default clues that are recorded when using :func:`Detective.default <deduce.clues.Detective.default>`."""


class Detective:
    """A gatherer of clues. Truly a know-it-all."""

    def __init__(self):
        self._records: Dict[Any, Converter] = {}

    @classmethod
    def default(cls) -> "Detective":
        """Build and return the default detective.

        This detective has clues about converters defined in
        the ``clues`` module.

        Returns
        -------
        detective : Detective
        """
        detective = cls()
        for clue, converter in CLUES.items():
            detective.record(clue, converter)
        return detective

    def record(self, clue: Hashable, converter: Converter):
        """Record a new clue about a converter.

        From now, the detective will know which converter to use when they see
        this clue.

        Parameters
        ----------
        clue : hashable (str, function, tuple, etc.)
        converter : Converter
        """
        self._records[clue] = converter

    def clue(self, clue: Hashable):
        """Record a clue about the decorated converter.

        See Also
        --------
        record
        """

        def decorate(func):
            self.record(clue, func)
            return func

        return decorate

    def retrieve(self, clue: T) -> Union[Converter, T]:
        """Retrieve the converter that corresponds to a clue.

        Parameters
        ----------
        clue : hashable (str, function, tuple, etc.)

        Returns
        -------
        converter : Converter or None
            This is `None` if no converter is recorded for `clue`.
        """
        return self._records.get(clue, clue)

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
            self.retrieve(value) for value in clues_or_converters
        ]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
