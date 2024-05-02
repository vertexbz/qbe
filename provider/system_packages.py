from __future__ import annotations

from dataclasses import dataclass
import os
from typing import TYPE_CHECKING

from . import provider
from .base import Provider
from ..adapter.command import sudo
from ..adapter.dataclass import field

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress

package_manager = 'apt' if os.path.exists('/usr/bin/apt') else None


@dataclass
class SystemPackagesConfig:
    packages: list[str] = field(name=package_manager)

    @classmethod
    def decode(cls, data: dict):
        if package_manager is None:
            return cls(packages=[])

        return cls(packages=data.get(package_manager, []))


@provider
class SystemPackagesProvider(Provider[SystemPackagesConfig]):
    DISCRIMINATOR = 'system-packages'
    CONFIG = SystemPackagesConfig

    @staticmethod
    async def _is_apt_pkg_installed(package: str) -> bool:
        try:
            out = await sudo('/usr/bin/dpkg-query --show --showformat=\'${db:Status-Status}\' ' + package, strip=True)
            return out.lower() == 'installed'
        except:
            return False

    async def apply(self, progress: IProviderProgress):
        if self._config and self._config.packages:
            if package_manager == 'apt':
                requirements = [
                    requirement for requirement in self._config.packages
                    if not await self._is_apt_pkg_installed(requirement)
                ]

                if len(requirements) > 0:
                    progress.log('installing system packages...')
                    await sudo('/usr/bin/apt install -y ' + ' '.join(requirements), stdout_callback=progress.log)
                    progress.log_changed('installed')
                else:
                    progress.log_unchanged('up to date')
            else:
                raise ValueError('unsupported package manager')

    @property
    def files(self) -> list[str]:
        return []

    async def remove(self, progress: IProviderProgress):
        pass  # something else may use, leaving for now
