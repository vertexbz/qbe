from __future__ import annotations

from typing import TYPE_CHECKING

from . import provider
from .operation import LinkConfig, OperationMixin
from ..paths import paths
from ..trigger.service_reload import ServiceReloadTrigger

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress


@provider
class KlipperExtensionProvider(OperationMixin[LinkConfig]):
    DISCRIMINATOR = 'klipper-screen-theme'
    CONFIG = LinkConfig

    async def apply(self, progress: IProviderProgress):
        if await self.apply_operations(progress, paths.klipper_screen.themes):
            progress.notify(ServiceReloadTrigger('KlipperScreen.service', restart=True))

    async def remove(self, progress: IProviderProgress):
        if await self.remove_operations(progress):
            progress.notify(ServiceReloadTrigger('KlipperScreen.service', restart=True))
