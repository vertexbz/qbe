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
