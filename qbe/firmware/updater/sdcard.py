from __future__ import annotations

import os.path
from typing import TYPE_CHECKING

from qbe.firmware.updater.base import BaseUpdater
from . import firmware_updater
from ...support import Command
from ...support import services

if TYPE_CHECKING:
    from qbe.config.mcu import AnyMCU


@firmware_updater('sdcard')
class SDCardUpdater(BaseUpdater):
    def flash(self, mcu: AnyMCU, firmware_path: str):
        sdcard_flash = Command(
            os.path.join(services.klipper.srcdir, 'scripts', 'flash-sdcard.sh'),
            args=['-f'],
            cwd=services.klipper.srcdir
        )

        raise NotImplemented('wip')
        sdcard_flash.piped([firmware_path, 'device', 'board'])  # TODO mapping


__all__ = []
