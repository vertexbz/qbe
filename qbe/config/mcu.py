from __future__ import annotations

import os.path
from typing import Union

from qbe.utils import jinja


class BaseMCU:
    def __init__(self, preset: str, config: dict):
        self.preset = preset
        self.overrides = config.pop('overrides', {})

    @property
    def info(self):
        return {
            'overrides': self.overrides
        }

    @property
    def fw_name(self):
        return self.preset

    def render_config(self) -> str:
        preset_path = os.path.join('firmware-presets', self.preset + '.config')
        return jinja.render_file(preset_path, self.overrides)


class CanMCU(BaseMCU):
    def __init__(self, preset: str, config: dict):
        super().__init__(preset, config)
        self.can_id = str(config.pop('can-id'))

    @property
    def fw_name(self):
        return self.preset + '-' + self.can_id

    @property
    def info(self):
        return {'can-id': self.can_id, **super().info}


AVAILABLE_TYPES = {
    'can-id': CanMCU
}

AnyMCU = Union[CanMCU]


def build_mcu(config: dict) -> AnyMCU:
    for discriminator, cls in AVAILABLE_TYPES.items():
        if config.get(discriminator, None) is not None:
            return cls(config.pop('preset'), config)

    raise ValueError(f'invalid mcu configuration {config}')
