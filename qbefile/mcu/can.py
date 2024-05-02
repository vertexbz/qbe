from __future__ import annotations

from . import mcu
from .base import BaseMCU


@mcu
class CanMCU(BaseMCU):
    DISCRIMINATOR = 'can-id'

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.mode = 'can'

        self.can_id = str(config.pop('can-id'))
        self.interface = config.pop('interface', 'can0')
