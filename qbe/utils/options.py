from __future__ import annotations
from typing import Any


class OptionsAwareOperation:
    def __init__(self) -> None:
        self.only: dict[str, Any] = {}
        self.unless: dict[str, Any] = {}

    def available(self, options: dict[str, str]):
        if len(self.only) == 0 and len(self.unless) == 0:
            return True

        result = len(self.only) == 0
        for key, state in self.only.items():
            if options.get(key, None) == state:
                result = True
                break

        for key, state in self.unless.items():
            if options.get(key, None) == state:
                result = False
                break

        return result
