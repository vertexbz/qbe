from __future__ import annotations

from dataclasses import dataclass
import os
from typing import TYPE_CHECKING

from . import trigger
from .base import Trigger
from ..paths import paths

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress import ProgressRoot


@trigger('gcode')
@dataclass(frozen=True)
class GCodeTrigger(Trigger):
    gcode: str

    @classmethod
    def decode(cls, data: dict, **kw):
        return cls(gcode=data.get('gcode'))

    async def handle(self, progress: ProgressRoot, updatable: Updatable):
        klipper_tty = paths.klipper.serial
        if not os.path.exists(klipper_tty):
            progress.log('Klipper does not seem to be running, you may need to execute following command after start:')
            progress.log(self.gcode)
            return

        tty = os.open(klipper_tty, os.O_RDWR)
        os.write(tty, (self.gcode + '\n').encode('utf-8'))
