from __future__ import annotations

from typing import TYPE_CHECKING

from . import provider
from .operation import SystemOperationConfig, OperationMixin
from ..adapter.command import sudo_rm

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress
    from ..lockfile.provided.provider_provided import Entry


@provider
class SystemConfigProvider(OperationMixin[SystemOperationConfig]):
    DISCRIMINATOR = 'system-config'
    CONFIG = SystemOperationConfig

    async def apply(self, progress: IProviderProgress):
        await self.apply_operations(progress, '/')

    async def remove(self, progress: IProviderProgress):
        await self.remove_operations(progress)

    async def _remove_entry(self, entry: Entry):
        path = entry.output
        if not path.startswith('/'):
            raise RuntimeError('path must be absolute')
        await sudo_rm(path, force=True, recursive=True)
