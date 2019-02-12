from collections import OrderedDict, defaultdict
from functools import update_wrapper
from inspect import Parameter, signature
from typing import (
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Iterator,
    Generic,
)

from .converters import Converter
from .clues import Detective
from .typevars import V
from .exceptions import ConversionError


def _filter(
    parameters: Mapping[str, Parameter], required: bool
) -> Dict[str, Parameter]:
    # NOTE: `parameters` is an `OrderedDict` and so is this filtered dict,
    # which ensures that the order of parameters declared on `func` is kept
    # intact.
    return OrderedDict(
        {
            name: param
            for name, param in parameters.items()
            if (required and param.default is Parameter.empty)
            or (not required and param.default is not Parameter.empty)
        }
    )


class deduce(
    Generic[V]
):  # pylint: disable=invalid-name, unsubscriptable-object
    """Build a deduced version of a function.

    Parameters
    ----------
    func : callable
    detective : Detective, optional
        A ``Detective`` object which has clues about which converters are
        available. Defaults to ``Detective.default``.

    Returns
    -------
    deduced : callable
        Wrapper of ``func`` that applies converters to positional and keyword
        parameters that have a type annotation.
    """

    def __init__(
        self, func: Callable[..., V], detective: Optional[Detective] = None
    ):
        self.func = func
        self.params = signature(func).parameters
        self.detective: Detective = (
            detective if detective is not None else Detective.default()
        )
        self.positional_converters: List[Tuple[str, Converter]] = []
        self.keyword_converters: Dict[str, Converter] = defaultdict(
            # Default to `identity` so that given kwargs that are not expected
            # by `func` are passed unchanged to `func` for failure.
            lambda: Converter.identity
        )
        self._build_converters()
        update_wrapper(self, self.func)

    @property
    def _required_params(self) -> dict:
        return _filter(self.params, required=True)

    @property
    def _optional_params(self) -> dict:
        return _filter(self.params, required=False)

    def _build_converters(self):
        self._build_positional_converters()
        self._build_keyword_converters()

    def _build_positional_converters(self):
        for param in self._required_params.values():
            name = param.name
            converter = (
                Converter.identity
                if param.annotation is Parameter.empty
                else self.detective.retrieve(param.annotation)
            )
            self.positional_converters.append((name, converter))

    def _build_keyword_converters(self):
        for name, param in self._optional_params.items():
            if param.annotation is not Parameter.empty:
                self.keyword_converters[name] = self.detective.retrieve(
                    param.annotation
                )

    def convert(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        errors: Dict[str, str] = {}

        converted_args = []
        fallbacks: Iterator[Tuple[str, Converter]] = iter(
            self.keyword_converters.items()
        )

        for i, value in enumerate(args):
            name: str
            converter: Converter
            try:
                name, converter = self.positional_converters[i]
            except IndexError:
                name, converter = next(fallbacks)

            try:
                converted_args.append(converter(value))
            except ValueError as exc:
                errors[name] = str(exc)

        converted_kwargs = {}

        for name, value in kwargs.items():
            try:
                converted_kwargs[name] = self.keyword_converters[name](value)
            except ValueError as exc:
                errors[name] = str(exc)

        if errors:
            raise ConversionError(**errors)

        return tuple(converted_args), converted_kwargs

    def __call__(self, *args, **kwargs) -> V:
        try:
            converted_args, converted_kwargs = self.convert(args, kwargs)
        except ConversionError as exc:
            raise exc from None
        else:
            return self.func(*converted_args, **converted_kwargs)
