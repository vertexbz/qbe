from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
import pathlib

from qbe.firmware.updater.base import BaseUpdater
from qbe.support.canboot import create_socket
from . import firmware_updater

if TYPE_CHECKING:
    from qbe.config.mcu import CanMCU


@firmware_updater('canboot')
class CanUpdater(BaseUpdater):
    def flash(self, mcu: CanMCU, firmware_path: str):
        if not hasattr(mcu, 'can_id') or not hasattr(mcu, 'interface'):
            raise ValueError('invalid mcu')

        loop = asyncio.new_event_loop()
        try:
            sock = create_socket(loop)
        except ModuleNotFoundError as e:
            loop.close()
            raise e
        except:
            loop.close()
            raise ConnectionError('failed acquiring can interface')

        try:
            loop.run_until_complete(
                sock.run(mcu.interface, int(mcu.can_id, 16), pathlib.Path(firmware_path), False)
            )
        finally:
            sock.close()
            loop.close()


__all__ = []
