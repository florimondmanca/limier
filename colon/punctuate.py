from collections import OrderedDict, defaultdict
from functools import update_wrapper
from inspect import Parameter, signature
from typing import Callable, Dict, List, Mapping, Optional, Tuple, Iterator

from .converters import Converter
from .registry import Registry
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


class punctuate:  # pylint: disable=invalid-name
    """Build a punctuated version of a function.

    Parameters
    ----------
    func : callable
    registry : Registry, optional
        A `Registry` object. Defaults to the default registry.

    Returns
    -------
    punctuated : callable
        Wrapper of `func` that applies converters to arguments and
        keyword arguments that have a type annotation.
    """

    def __init__(
        self, func: Callable[..., V], registry: Optional[Registry] = None
    ):
        self.func = func
        self.params = signature(func).parameters
        self.registry = registry if registry is not None else Registry.default()
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
                else self.registry.get(param.annotation)
            )
            self.positional_converters.append((name, converter))

    def _build_keyword_converters(self):
        for name, param in self._optional_params.items():
            if param.annotation is not Parameter.empty:
                self.keyword_converters[name] = self.registry.get(
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
