from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

from .config import MCUConfigManifest
from ...adapter.dataclass import field
from ...adapter.file import readfile
from ...adapter.yaml import load as load_yaml
from ...paths import paths


@dataclass(frozen=True)
class Manifest:
    """QBE MCU Manifest"""
    name: str
    mode: dict[str, MCUConfigManifest] = field(default_factory=dict)
    flash: list[str] = field(default_factory=list)

    def mode_config(self, mode: Optional[str]) -> MCUConfigManifest:
        return self.mode[self.mode_key(mode)]

    def mode_key(self, mode: Optional[str]) -> str:
        return mode or next(iter(self.mode))

    @classmethod
    def decode(cls, data: dict) -> Manifest:
        flash = data.get('flash', [])
        if isinstance(flash, str):
            flash = [flash]

        return cls(
            name=data.get('name'),
            mode={k: MCUConfigManifest.decode(v) for k, v in data.get('mode').items()},
            flash=flash
        )


def load(preset: str) -> Manifest:
    return Manifest.decode(load_yaml(readfile(os.path.join(paths.qbe.mcu_preset(preset), 'mcu.yml'))))
