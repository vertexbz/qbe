from __future__ import annotations

from typing import TYPE_CHECKING

from . import provider
from .operation import OperationConfig, OperationMixin
from ..paths import paths
from ..trigger.service_reload import ServiceReloadTrigger

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress


@provider
class MoonrakerConfigProvider(OperationMixin[OperationConfig]):
    DISCRIMINATOR = 'moonraker-config'
    CONFIG = OperationConfig

    async def apply(self, progress: IProviderProgress):
        if await self.apply_operations(progress, paths.moonraker.configs, paths.moonraker.config_links):
            progress.notify(ServiceReloadTrigger('moonraker.service', restart=True))

    async def remove(self, progress: IProviderProgress):
        if await self.remove_operations(progress):
            progress.notify(ServiceReloadTrigger('KlipperScreen.service', restart=True))
