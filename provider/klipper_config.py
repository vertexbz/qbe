from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from . import provider
from .operation import OperationConfig, OperationMixin
from ..paths import paths
from ..trigger.gcode import GCodeTrigger

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress


@dataclass
class TargetPath:
    main: str
    link: Optional[str] = None


@provider
class KlipperConfigProvider(OperationMixin[OperationConfig]):
    DISCRIMINATOR = 'klipper-config'
    CONFIG = OperationConfig

    async def apply(self, progress: IProviderProgress):
        if await self.apply_operations(progress, paths.klipper.configs, paths.klipper.config_links):
            progress.notify(GCodeTrigger('FIRMWARE_RESTART'))

    async def remove(self, progress: IProviderProgress):
        if await self.remove_operations(progress):
            progress.notify(GCodeTrigger('FIRMWARE_RESTART'))
