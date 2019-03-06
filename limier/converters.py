import re
from typing import (
    Callable,
    Dict,
    Generic,
    Match,
    Optional,
    Pattern,
    Tuple,
    Type,
    Union,
)

from .typevars import T, U, V, W  # pylint: disable=unused-import

__all__ = (
    "Converter",
    "Filter",
    "Transform",
    "Equiv",
    "OneOf",
    "Regex",
    "Range",
)


class Converter(Generic[T, V]):  # pylint: disable=unsubscriptable-object
    """Class-style definition of the base converter interface.

    A converter is basically a callable that:
    
    1. Takes an input ``value``.
    2. Converts it and raises ``ValueError`` in case any validation fails.
    3. Returns the converted value.

    The input and converted values do not have to be of the same type.

    .. note::
        Concrete subclasses should implement ``__call__(self, value)``.
    """

    def __call__(self, value: T) -> V:
        raise NotImplementedError


class Filter(Converter[T, T]):
    """Raise ``ValueError`` if ``test(value)`` evaluates to ``False``.

    Parameters
    -----------
    test : callable
        a function that should evaluate to `True` if the given value
        is valid, `False` otherwise.

    Example
    -------
    >>> f = Filter(str.islower)
    >>> f("hello")
    "hello"
    >>> f("Hello")
    ValueError: 'Hello' does not satisfy 'islower'
    """

    def __init__(self, test: Callable[[T], bool]):
        self.test = test

    def get_failure_message(self, value: T) -> str:
        """The message to bundle with ``ValueError`` when the test failed."""
        try:
            return f"'{value}' does not satisfy '{self.test.__name__}'"
        except AttributeError:
            return str(value)

    def __call__(self, value: T) -> T:
        if not self.test(value):
            raise ValueError(self.get_failure_message(value))
        return value


class Transform(Converter[T, V]):
    """Transform the input value using a function.

    This converter is typically used to wrap a callable that may not
    always raise ``ValueError`` when it fails to process the input ``value``,
    or in conjunction with ``functools.partial``.

    Parameters
    ------------
    transformation : callable
    raised_if_invalid : class
        The exception that `transformation` raises in case of an invalid
        value. Defaults to `ValueError`.

    Example
    -------
    >>> from decimal import Decimal, InvalidOperation
    >>> to_decimal = Transform(Decimal, raised_if_invalid=InvalidOperation)
    >>> to_decimal("1.5")
    Decimal('1.5')
    42
    >>> to_decimal("oops")
    ValueError: [<class 'decimal.ConversionSyntax'>]
    """

    def __init__(
        self,
        transformation: Callable[[T], V],
        raised_if_invalid: Type[BaseException] = ValueError,
    ):
        self.transformation = transformation
        self.raised_if_invalid = raised_if_invalid

    def __call__(self, value: T) -> V:
        try:
            return self.transformation(value)
        except self.raised_if_invalid as exc:
            raise ValueError(str(exc)) from exc


class OneOf(Filter[T]):
    """Require that the input value is one among a given set.

    Parameters
    ----------
    *values : any
        values which the input value must be one of.
        Must be hashable since a `set` is built out of
        them for faster `in` lookup.

    Example
    -------
    >>> accepted_fruits = OneOf("apple", "orange", "strawberrie")
    >>> accepted_fruits("apple")
    "apple"
    >>> accepted_fruits("watermelon")
    ValueError: expected one of 'orange, apple', got 'watermelon'
    """

    def __init__(self, *values: T):
        self.values = set(values)

        def test(value: T) -> bool:
            return value in self.values

        super().__init__(test=test)

    def get_failure_message(self, value: T) -> str:
        values = ", ".join(map(str, self.values))
        return f"expected one of '{values}', got '{value}'"


class Equiv(Converter[T, V]):
    """Map input values to equivalents.

    The name ``Equiv`` was chosen to prevent conflicts with ``typing.Mapping``.

    Parameters
    ----------
    mapping : dict
        A mapping of values to their equivalent.

        .. tip::
            Bulk mapping is supported by using tuples as keys. Then, all values
            in map to the tuple's equivalent (see the example below).

    Raises
    ------
    ``ValueError``:
        If no equivalent exists for ``value``.

    Example
    -------
    >>> as_bool = Equiv({
        # Single mapping
        "true": True,
        "True": True,
        # Bulk mapping
        ("False", "false"): False,
    })
    >>> as_bool("true")
    True
    >>> as_bool("False")
    False
    >>> truths("sure")
    ValueError: no equivalent for 'sure'
    """

    def __init__(self, mapping: Dict[Union[T, Tuple[T]], V]):
        _mapping = {}
        for key, value in mapping.items():
            if isinstance(key, tuple):
                for sub_key in key:
                    _mapping[sub_key] = value
                continue
            _mapping[key] = value

        self.mapping = _mapping

    def __call__(self, value: T) -> V:
        try:
            return self.mapping[value]
        except KeyError as exc:
            raise ValueError(f"no equivalent for '{value}'") from exc


class Regex(Converter[str, V]):
    """Match based on a regular expression and convert the matched value.

    Parameters
    ----------
    pattern : str or re.Pattern
        a regular expression pattern that is compiled for faster matching.
        Also accepted as a class attribute.
    kwargs : any
        additional keyword arguments passed to ``re.compile()``.
    """

    def __init__(self, pattern: Optional[Union[str, Pattern]] = None, **kwargs):
        if pattern is None:
            try:
                pattern = self.pattern
            except AttributeError as exc:
                raise ValueError(
                    "`pattern` not given and not defined "
                    "on the regex converter class."
                ) from exc
        self._pattern: Pattern = re.compile(pattern, **kwargs)

    @property
    def pattern(self) -> Pattern:
        return self._pattern

    def convert(self, match: Match) -> V:  # pylint: disable=no-self-use
        """Build the output value out of the ``re.Match`` object.

        Returns
        -------
        value : any
            The matched string by default.
        """
        return match.string

    def __call__(self, value: str) -> V:
        match = self._pattern.match(value)
        if match is None:
            raise ValueError(
                f"did not match '{self._pattern.pattern}': '{value}'"
            )
        return self.convert(match)


class Range(Regex[range]):
    """Build a Python ``range`` object from the input value.

    Supported formats:

    - ``{min}:{max}``
    - ``{min}..{max}``
    - ``{min}...{max}``
    """

    pattern = re.compile(r"(\d+)(?:\.{2,3}|:)(\d+)")

    def convert(self, match: Match) -> range:
        return range(int(match.group(1)), int(match.group(2)))
