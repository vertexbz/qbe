from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
from typing import TYPE_CHECKING

from ...adapter.command import shell
from ...adapter.file import writefile, readfile
from ...adapter.jinja import render
from ...paths import paths
from ...provider.base import Provider
from ...updatable.progress.formatter import MessageType

if TYPE_CHECKING:
    from ...updatable.progress.provider.interface import IProviderProgress
    from ...lockfile.provided.entry import Entry
    from .. import MCU


@dataclass
class FirmwareConfig:
    output_file: str


class FirmwareProvider(Provider[FirmwareConfig]):
    DISCRIMINATOR = 'firmware'
    CONFIG = FirmwareConfig

    _updatable: MCU

    @property
    def template_path(self):
        preset_dir = paths.qbe.mcu_preset(self._updatable.config.preset)
        template_file = str(os.path.join(preset_dir, self._updatable.mode_config.firmware))
        if not os.path.exists(template_file):
            raise ValueError('Cannot load firmware config template')
        return template_file

    async def apply(self, progress: IProviderProgress):
        if not os.path.exists(self.template_path):
            raise ValueError('Cannot load firmware config template')

        env = dict(os.environ)

        if not os.path.exists(self._config.output_file) or self._updatable.options_dirty:
            progress.log(f'Building {self._updatable.manifest.name} firmware for {self._updatable.name}...')

            target_path = os.path.join(paths.klipper.pkg, 'out', 'klipper.bin')
            target_config = os.path.join(paths.klipper.pkg, '.config')

            progress.log(f'Preparing config...')
            writefile(target_config, render(readfile(self.template_path), self._updatable.options))

            progress.log(f'Preparing sources dir...')
            await shell('/usr/bin/make clean', cwd=paths.klipper.pkg, env=env, stdout_callback=progress.log)

            try:
                progress.log(f'Building firmware...')
                await shell('/usr/bin/make', cwd=paths.klipper.pkg, env=env, stdout_callback=progress.log)
                shutil.copyfile(target_path, self._config.output_file)
            finally:
                if os.path.exists(target_config):
                    os.unlink(target_config)

            with progress.sub(os.path.basename(self._config.output_file), case=True) as p:
                p.log_changed('built', input=self.template_path, output=self._config.output_file)
        else:
            with progress.sub(os.path.basename(self._config.output_file), case=True) as p:
                p.log_unchanged('already exists', input=self.template_path, output=self._config.output_file)

        self._cleanup(progress, progress.untouched)

    @property
    def files(self) -> list[str]:
        return [self.template_path]

    async def remove(self, progress: IProviderProgress):
        self._cleanup(progress, progress.provided)

    @staticmethod
    def _cleanup(progress: IProviderProgress, entries: set[Entry]):
        for entry in list(entries):
            with progress.sub(os.path.basename(entry.output), case=True) as p:
                if os.path.exists(entry.output):
                    os.unlink(entry.output)
                    p.log_removed('removed', entry)
                else:
                    p.log_removed('absent', entry, typ=MessageType.INFO)
