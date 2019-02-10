from functools import reduce
from typing import Any, Callable, Dict, Hashable, List, Union

from .converters import Converter, Transform
from .defaults import DEFAULT_CONVERTERS
from .typevars import T, V


class Registry:
    """A registry of converters.

    Defines methods that are pre-bound at the module level.
    """

    def __init__(self):
        self._aliases: Dict[Any, Converter] = {}

    @classmethod
    def from_defaults(cls) -> "Registry":
        registry = cls()
        for alias, converter in DEFAULT_CONVERTERS.items():
            registry.register(alias, converter)
        return registry

    def register(self, alias: Hashable, converter: Converter):
        self._aliases[alias] = converter

    def get(
        self, obj: Union[Converter[T, V], Callable[[T], V]]
    ) -> Converter[T, V]:
        if isinstance(obj, Converter):
            return obj
        try:
            return self._aliases[obj]
        except KeyError:
            return Transform(obj)

    def chain(self, *args: Union[Converter, Any]) -> Converter:
        converters: List[Converter] = [self.get(arg) for arg in args]

        def convert(value: str) -> Any:
            return reduce(
                lambda val, converter: converter(val), converters, value
            )

        return Transform(convert)
