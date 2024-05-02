from __future__ import annotations

from functools import cached_property
import hashlib
import os
from typing import TYPE_CHECKING, Optional

from .manifest import load
from .provider.firmware import FirmwareProvider, FirmwareConfig
from .provider.flash import FlashProvider, FlashConfig
from ..paths import paths
from ..trigger.gcode import GCodeTrigger
from ..updatable import Updatable
from ..updatable.data_source.mcu import MCUDataSource

if TYPE_CHECKING:
    from updatable.progress import UpdatableProgress
    from ..qbefile.mcu import BaseMCU
    from ..lockfile.mcu import MCULock


class MCU(Updatable):
    def __init__(self, config: BaseMCU, lock: MCULock):
        super().__init__(lock)
        self._config = config
        self._source = MCUDataSource(os.path.join(paths.packages, 'klipper'))

    @cached_property
    def manifest(self):
        return load(self._config.preset)

    @property
    def lock(self) -> MCULock:
        return super().lock  # type: ignore

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def type(self) -> Optional[str]:
        return 'firmware'

    @property
    def options(self) -> dict:
        return self._config.options

    @property
    def options_dirty(self) -> bool:
        return self._config.options != self.lock.current_options

    @property
    def recipie_dirty(self) -> bool:
        return False  # never dirty, hardcoded

    @property
    def config(self):
        return self._config

    @property
    def mode_config(self):
        return self.manifest.mode_config(self._config.mode)

    @property
    def flash_mode(self):
        if self.mode_config.bootloader:
            return self.mode_config.bootloader.type

        if self._config.mode:
            return self._config.mode

        return self.manifest.flash[0]

    async def update(self, progress: UpdatableProgress, build_only: bool = False, **kw) -> None:
        await super().update(progress, **kw)  # (actually no) pull

        opts_hash = hashlib.sha256(str(self.options).encode('utf-8')).hexdigest()[:8]
        mode = self.manifest.mode_key(self._config.mode)
        output_file_name = f'{self.name.lower()}-{mode}-{self.version.remote}-{opts_hash}.bin'
        output_file = str(os.path.join(paths.firmwares, output_file_name))

        firmware_provider = FirmwareProvider(self, FirmwareConfig(output_file=output_file))
        with progress.provider(firmware_provider) as p:
            await firmware_provider.apply(p)

        if not build_only:
            flash_provider = FlashProvider(self, FlashConfig(firmware_path=output_file))
            with progress.provider(flash_provider) as p:
                await flash_provider.apply(p)

        if progress.updated or progress.installed:
            progress.notify(GCodeTrigger('FIRMWARE_RESTART'))

        self.lock.current_options = self._config.options
        if not build_only:
            self.lock.current_version = self.lock.remote_version
            self.lock.commits_behind = []
