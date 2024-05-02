from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from ....qbefile.mcu.base import BaseMCU


class Flasher:
    def __init__(self):
        pass

    @abstractmethod
    async def flash(self, mcu: BaseMCU, firmware_path: str, stdout_callback: Optional[Callable[[str], None]] = None):
        pass
