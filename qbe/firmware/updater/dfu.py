from __future__ import annotations
from typing import TYPE_CHECKING

from qbe.firmware.updater.base import BaseUpdater
from . import firmware_updater
from ...support import Command

if TYPE_CHECKING:
    from qbe.config.mcu import AnyMCU


@firmware_updater('dfu')
class DfuUpdater(BaseUpdater):
    def flash(self, mcu: AnyMCU, firmware_path: str):
        dfu_util = Command(
            '/usr/bin/dfu-util',
            # TODO ["-p", buspath] instead of -d ?
            args=['-a', '0', '--dfuse-address', '0x08000000:force:mass-erase:leave', '-d', '0483:df11', '-D'],
            cwd=self.config.paths.firmwares
        )

        dfu_util.piped([firmware_path])


__all__ = []
