import decimal
from functools import partial
from typing import Any, Dict

from .converters import Converter, Equiv, Filter, Range, Transform


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
"""Default aliases that are recorded when using :func:`Registry.default <limier.registry.Registry.default>`."""
