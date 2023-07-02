from __future__ import annotations
from typing import TYPE_CHECKING

from qbe.config.mcu.base import BaseMCU

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class CanMCU(BaseMCU):
    def __init__(self, preset: str, config: dict, paths: ConfigPaths):
        super().__init__(preset, config, paths)
        self.can_id = str(config.pop('can-id'))
        self.interface = config.pop('interface', 'can0')
        self.mode = 'can'

    @property
    def info(self):
        return {'can-id': self.can_id, 'interface': self.interface, **super().info}
