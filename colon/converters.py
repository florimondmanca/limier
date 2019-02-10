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
    """Base converter interface."""

    identity: "Identity"

    def __call__(self, value: T) -> V:
        raise NotImplementedError


class Identity(Converter[T, T]):
    """The no-op converter that returns what it's given."""

    def __call__(self, value: T) -> T:
        return value


Converter.identity = Identity()


class Filter(Converter[T, T]):
    """Require that the inbound value passes a test.

    Parameters
    -----------
    test : callable
        a function that should evaluate to `True` if the given value
        is valid, `False` otherwise.
    """

    def __init__(self, test: Callable[[T], bool]):
        self.test = test

    def get_message(self) -> str:
        return "did not pass '{self.test.__name__}'"

    def __call__(self, value: T) -> T:
        if not self.test(value):
            raise ValueError(f"{self.get_message()}: '{value}'")
        return value


class Transform(Converter[T, V]):
    """Transform the inbound value.

    Parameters
    ------------
    transformation : callable
    exception_cls : class
        The exception that `transformation` raises in case of an invalid
        value. Defaults to `ValueError`.
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
            raise ValueError(
                f"could not convert using {self.transformation.__name__}: "
                f"'{value}'"
            ) from exc


class OneOf(Filter[T]):
    """Require that the inbound value is one among a given set.

    Parameters
    ----------
    *values : any
        values which the inbound value must be one of.
        Must be hashable since a `set` is built out of
        them for faster `in` lookup.
    """

    def __init__(self, *values: T):
        self.values = set(values)

        def test(value: T) -> bool:
            return value in self.values

        super().__init__(test=test)

    def get_message(self) -> str:
        return f"expected one of of {', '.join(map(str, self.values))}"


class Mapping(Converter[T, V]):
    """Convert map equivalent values to a normalized value.

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
    ValueError
    """

    def __init__(self, mapping: Dict[V, Set[T]]):
        self.mapping = mapping

    def __call__(self, value: T) -> V:
        for val, values in self.mapping.items():
            if value in values:
                return val
        raise ValueError(
            "cannot interpret as one of "
            f"{', '.join(map(str, self.mapping))}: '{value}'"
        )


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