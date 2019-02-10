import re
from typing import (
    Callable,
    Dict,
    Generic,
    Match,
    Optional,
    Pattern,
    Set,
    Type,
    Union,
)

from .typevars import T, U, V, W  # pylint: disable=unused-import


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

    identity: "Identity"

    def __call__(self, value: T) -> V:
        raise NotImplementedError


class Identity(Converter[T, T]):
    """The no-op converter that returns what it's given.

    This is typically used as a default when no other converter is available.
    """

    def __call__(self, value: T) -> T:
        return value


Converter.identity = Identity()


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
    """Transform the inbound value using a function.

    This is the simplest kind of converters which is typically used to wrap
    a callable that may not always return ``ValueError`` when it fails to
    process the input ``value``.

    Parameters
    ------------
    transformation : callable
    exception_cls : class
        The exception that `transformation` raises in case of an invalid
        value. Defaults to `ValueError`.

    Example
    -------
    >>> from functools import partial
    >>> from_binary = Transform(partial(int, base=2))
    >>> from_binary("10101")
    42
    >>> from_binary("1234")
    ValueError: invalid literal for int() with base 2: '1234'
    """

    def __init__(
        self,
        transformation: Callable[[T], V],
        exception_cls: Type[BaseException] = ValueError,
    ):
        self.transformation = transformation
        self.exception_cls = exception_cls

    def __call__(self, value: T) -> V:
        try:
            return self.transformation(value)
        except self.exception_cls as exc:
            raise ValueError(str(exc)) from exc


class OneOf(Filter[T]):
    """Require that the inbound value is one among a given set.

    Parameters
    ----------
    *values : any
        values which the inbound value must be one of.
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


class Mapping(Converter[T, V]):
    """Map equivalent values to a normalized value.

    Parameters
    ----------
    mapping : dict
        a dict mapping normalized values to strings that represent them.

    Example
    -------
    >>> truths = Mapping({True: {"true", "True", "yes", "y", "1"}})
    >>> truths("true")
    True
    >>> truths("sure")
    ValueError: 'sure' is not equivalent to any known value
    """

    def __init__(self, mapping: Dict[V, Set[T]]):
        self.mapping = mapping

    def __call__(self, value: T) -> V:
        for val, values in self.mapping.items():
            if value in values:
                return val
        raise ValueError(f"'{value}' is not equivalent to any known value")


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
    """Build a Python ``range`` object from the inbound value.

    Supported formats:

    - ``{min}:{max}``
    - ``{min}..{max}``
    - ``{min}...{max}``
    """

    pattern = re.compile(r"(\d+)(?:\.{2,3}|:)(\d+)")

    def convert(self, match: Match) -> range:
        return range(int(match.group(1)), int(match.group(2)))
