import decimal
from functools import partial
from typing import Any, Dict

from .converters import Converter, Filter, Mapping, Range, Transform

DEFAULT_CONVERTERS: Dict[Any, Converter] = {
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
        decimal.Decimal, exception_cls=decimal.InvalidOperation
    ),
    # Mappings
    bool: Mapping(
        {
            True: {"true", "True", "yes", "1"},
            False: {"false", "False", "no", "0"},
        }
    ),
    None: Mapping({None: {"null", "none"}}),
    # Other
    range: Range(),
}
