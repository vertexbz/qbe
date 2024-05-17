from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import provider
from .operation import LinkConfig, OperationMixin
from ..paths import paths
from ..trigger.service_reload import ServiceReloadTrigger

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress


@provider
class MoonrakerExtensionProvider(OperationMixin[LinkConfig]):
    DISCRIMINATOR = 'moonraker-extension'
    CONFIG = LinkConfig

    async def apply(self, progress: IProviderProgress):
        if await self.apply_operations(progress, paths.moonraker.extensions):
            progress.notify(ServiceReloadTrigger('moonraker.service', restart=True))

    async def remove(self, progress: IProviderProgress):
        if await self.remove_operations(progress):
            progress.notify(ServiceReloadTrigger('moonraker.service', restart=True))

    def _sub_name(self, operation, source: str, target: str):
        return f'{self._short_path(operation.source, source, True)} -> {os.path.basename(target)}'
