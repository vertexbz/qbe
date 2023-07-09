from __future__ import annotations

import os.path
from typing import TYPE_CHECKING

from qbe.firmware.updater.base import BaseUpdater
from . import firmware_updater
from ...support import Command
from ...support import services

if TYPE_CHECKING:
    from qbe.config.mcu import AnyMCU


@firmware_updater('rp2040')
class RP2040Updater(BaseUpdater):
    def flash(self, mcu: AnyMCU, firmware_path: str):
        executable = os.path.join(services.klipper.srcdir, 'lib', 'rp2040_flash', 'rp2040_flash')
        if not os.path.exists(executable):
            Command(
                '/usr/bin/make',
                cwd=os.path.dirname(executable)
            ).piped([])

        rp2040_flash = Command(
            executable,
            cwd=self.config.paths.firmwares
        )

        rp2040_flash.piped([firmware_path])  # TODO ..., bus, addr]


__all__ = []
