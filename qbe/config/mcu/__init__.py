from __future__ import annotations

from typing import Union, TYPE_CHECKING

from qbe.config.mcu.can import CanMCU

if TYPE_CHECKING:
    from qbe.config import ConfigPaths

AVAILABLE_TYPES = {
    'can-id': CanMCU
}

AnyMCU = Union[CanMCU]


def build_mcu(config: dict, paths: ConfigPaths) -> AnyMCU:
    for discriminator, cls in AVAILABLE_TYPES.items():
        if config.get(discriminator, None) is not None:
            return cls(config.pop('preset'), config, paths)

    raise ValueError(f'invalid mcu configuration {config}')
