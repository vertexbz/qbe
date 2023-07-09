from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.config.mcu import AnyMCU
    from qbe.config import Config


class BaseUpdater:
    def __init__(self, config: Config):
        self.config = config

    def flash(self, mcu: AnyMCU, firmware_path: str):
        pass
