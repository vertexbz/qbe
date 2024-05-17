from __future__ import annotations

from typing import Optional


class BaseMCU:
    DISCRIMINATOR: Optional[str] = None

    def __init__(self, name: str, config: dict):
        self.name = name
        self.mode = None

        self.preset = config.pop('preset')
        self.main = config.pop('main', False)
        self.options = config.pop('options', {})

    def update(self, source: BaseMCU) -> None:
        if type(self) is not type(source):
            raise TypeError('Update source MCU must be the same type!')

        self.mode = source.mode
        self.preset = source.preset
        self.main = source.main
        self.options = source.options
