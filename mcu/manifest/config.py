from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from .config_bootloader import MCUConfigBootloaderManifest


@dataclass(frozen=True)
class MCUConfigManifest:
    """QBE MCU Mode Manifest"""
    firmware: str
    bootloader: Optional[MCUConfigBootloaderManifest] = None

    @classmethod
    def decode(cls, data: Union[str, dict]) -> MCUConfigManifest:
        if isinstance(data, str):
            return cls(firmware=data)

        bootloader: Optional[dict] = data.get('bootloader', None)
        return cls(
            firmware=data.get('firmware'),
            bootloader=MCUConfigBootloaderManifest.decode(bootloader) if bootloader else None
        )
