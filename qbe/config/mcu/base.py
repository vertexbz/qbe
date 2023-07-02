from __future__ import annotations
import os.path
from typing import TYPE_CHECKING

from qbe.config.mcu.definition import MCUDefinition

from qbe.firmware import MCUFirmware
from qbe.support import services

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class BaseMCU:
    def __init__(self, preset: str, config: dict, paths: ConfigPaths):
        self.preset = preset
        self.name = config.pop('name', preset)
        self.definition = MCUDefinition.from_preset_name(preset)
        self.options = config.pop('options', {})

        self.mode = config.pop('mode', self.definition.default_mode)

        self.firmware = MCUFirmware(
            paths.firmwares, preset, self.mode,
            self.definition.modes[self.mode].firmware, self.options,
            services.klipper.srcdir if services.klipper is not None else None
        )

        self.bootloader = None
        if self.definition.modes[self.mode].bootloader is not None:
            package_path = os.path.join(paths.packages, self.definition.modes[self.mode].bootloader_type)
            self.bootloader = MCUFirmware(
                paths.firmwares, preset, self.mode + '-' + self.definition.modes[self.mode].bootloader_type,
                self.definition.modes[self.mode].bootloader, self.options,
                package_path if os.path.isdir(package_path) else None
            )

    @property
    def info(self):
        return {
            'preset': self.preset,
            'mode': self.mode,
            'options': self.options
        }
