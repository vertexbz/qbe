from __future__ import annotations
import os.path
from enum import Enum
from typing import Union, TYPE_CHECKING

from qbe.support import services
from qbe.utils import jinja

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class MCUFwStatus(Enum):
    ABSENT = 0
    OUTDATED = 1
    BUILT = 2
    UP_TO_DATE = 3


class BaseMCU:
    def __init__(self, preset: str, config: dict, paths: ConfigPaths):
        self.preset = preset
        self.options = config.pop('options', {})
        self._target_dir = paths.firmwares

    @property
    def info(self):
        return {
            'options': self.options
        }

    @property
    def fw_name(self):
        return self.preset

    @property
    def fw_file(self):
        return self.fw_name + '.bin'

    @property
    def fw_path(self):
        return os.path.join(self._target_dir, self.fw_file)

    @property
    def fw_status(self) -> MCUFwStatus:
        if not os.path.exists(self.fw_path):
            return MCUFwStatus.ABSENT

        if services.klipper is None:
            return MCUFwStatus.OUTDATED

        klipper_head = os.path.join(services.klipper.srcdir, '.git', 'FETCH_HEAD')
        if os.path.getmtime(self.fw_path) < os.path.getmtime(klipper_head):
            return MCUFwStatus.OUTDATED

        return MCUFwStatus.BUILT

    def render_config(self) -> str:
        preset_path = os.path.join('firmware-presets', self.preset + '.config')
        return jinja.render_file(preset_path, self.options)


class CanMCU(BaseMCU):
    def __init__(self, preset: str, config: dict, paths: ConfigPaths):
        super().__init__(preset, config, paths)
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


def build_mcu(config: dict, paths: ConfigPaths) -> AnyMCU:
    for discriminator, cls in AVAILABLE_TYPES.items():
        if config.get(discriminator, None) is not None:
            return cls(config.pop('preset'), config, paths)

    raise ValueError(f'invalid mcu configuration {config}')
