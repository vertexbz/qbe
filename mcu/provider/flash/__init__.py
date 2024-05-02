from __future__ import annotations

from dataclasses import dataclass
import os
import pkgutil
from typing import TYPE_CHECKING, Type

from .base import Flasher
from ....paths import paths
from ....provider.base import Provider

if TYPE_CHECKING:
    from ....updatable.progress.provider.interface import IProviderProgress
    from ... import MCU


@dataclass
class FlashConfig:
    firmware_path: str


class FlashProvider(Provider[FlashConfig]):
    _flashers: dict[str, Type[Flasher]] = {}
    DISCRIMINATOR = 'flash'
    CONFIG = FlashConfig

    _updatable: MCU

    @classmethod
    def flasher(cls, name: str):
        def inner(wrapped: Type[Flasher]):
            if name in cls._flashers:
                raise ValueError(f'Name {name} already registered!')
            if not issubclass(wrapped, Flasher):
                raise ValueError(f'Class {wrapped} is not a subclass of {Flasher}')
            cls._flashers[name] = wrapped
            return wrapped

        return inner

    async def apply(self, progress: IProviderProgress):
        for entry in progress.provided:
            progress.forget(entry)

        short_path = self._config.firmware_path
        if self._config.firmware_path.startswith(paths.firmwares):
            short_path = os.path.relpath(self._config.firmware_path, paths.firmwares)

        if self._updatable.version.remote != self._updatable.version.local or self._updatable.options_dirty:
            mode = self._updatable.flash_mode
            if mode not in self._flashers:
                raise ValueError(f'Unsupported flash mode {mode}')

            progress.log(f'Flashing {self._updatable.name} firmware...')
            progress.log(f'Flash mode: {mode}')
            progress.log(f'Firmware file: {short_path}')

            flasher = self._flashers[mode]()
            await flasher.flash(self._updatable.config, self._config.firmware_path, stdout_callback=progress.log)
            progress.log_changed('flashed', input=self._config.firmware_path, output=None)
        else:
            progress.log_unchanged('up to date', input=self._config.firmware_path, output=None)

    @property
    def files(self) -> list[str]:
        return []

    async def remove(self, progress: IProviderProgress):
        pass  # no way


# Load Flashers
__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)
