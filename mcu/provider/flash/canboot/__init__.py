from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Optional, Callable

from .socket import CanSocket
from .. import FlashProvider
from ..base import Flasher

if TYPE_CHECKING:
    from .....qbefile.mcu.can import CanMCU


@FlashProvider.flasher('canboot')
class CanUpdater(Flasher):
    async def flash(self, mcu: CanMCU, firmware_path: str, stdout_callback: Optional[Callable[[str], None]] = None):
        if not mcu.interface:
            raise ValueError("The 'interface' option must be specified to flash a device")

        if not mcu.can_id:
            raise ValueError("The 'uuid' option must be specified to flash a device")

        if not os.path.isfile(firmware_path):
            raise ValueError(f"Invalid firmware path '{firmware_path}'")

        with CanSocket(asyncio.get_event_loop(), mcu.interface, stdout_callback=stdout_callback) as sock:
            uuid = int(mcu.can_id, 16)
            await sock.bootloader(uuid)
            await sock.flash(uuid, firmware_path)


__all__ = []
