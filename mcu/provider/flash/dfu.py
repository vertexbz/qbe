from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from . import FlashProvider
from .base import Flasher
from ....adapter.command import shell
from ....paths import paths

if TYPE_CHECKING:
    from ....qbefile.mcu.base import BaseMCU


@FlashProvider.flasher('dfu')
class DfuUpdater(Flasher):
    async def flash(self, mcu: BaseMCU, firmware_path: str, stdout_callback: Optional[Callable[[str], None]] = None):
        await shell(
            f'/usr/bin/dfu-util -a 0 --dfuse-address 0x08000000:force:mass-erase:leave -d 0483:df11 -D {firmware_path}',
            cwd=paths.firmwares,
            stdout_callback=stdout_callback
        )


__all__ = []
