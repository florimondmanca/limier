from typing import Dict


class ConversionError(Exception):
    def __init__(self, **errors):
        super().__init__()
        self.errors: Dict[str, str] = errors

    def __str__(self) -> str:
        return f"ConversionError: {self.errors}"
