from __future__ import annotations

from typing import TYPE_CHECKING

from . import provider
from .operation import OperationConfig, OperationMixin
from ..paths import paths

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress


@provider
class UserConfigProvider(OperationMixin[OperationConfig]):
    DISCRIMINATOR = 'user-config'
    CONFIG = OperationConfig

    async def apply(self, progress: IProviderProgress):
        await self.apply_operations(progress, paths.config_root)

    async def remove(self, progress: IProviderProgress):
        await self.remove_operations(progress)
