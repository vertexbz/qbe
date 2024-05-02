from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MCUConfigBootloaderManifest:
    """QBE MCU Mode Bootloader Manifest"""
    type: str
    config: str

    @classmethod
    def decode(cls, data: dict) -> MCUConfigBootloaderManifest:
        return cls(
            type=data.get('type'),
            config=data.get('config')
        )
