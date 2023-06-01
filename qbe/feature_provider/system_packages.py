from __future__ import annotations
import os
import time
from qbe.utils.obj import qrepr
from qbe.support import apt
import qbe.cli as cli
from .base import BaseProvider
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section

package_manager = 'apt' if os.path.exists('/usr/bin/apt') else None


class SystemPackagesProviderConfig:
    def __init__(self, **kw) -> None:
        if package_manager is not None:
            self.system_packages: dict[str, list[str]] = kw.pop(package_manager, None)

    __repr__ = qrepr()


@feature_provider('system-packages')
class SystemPackagesProvider(BaseProvider):
    @classmethod
    def validate_config(cls, config: dict) -> SystemPackagesProviderConfig:
        if not isinstance(config, dict):
            raise ValueError('Invalid configuration for moonraker-extension provider')
        return SystemPackagesProviderConfig(**config)

    def process(self, config: SystemPackagesProviderConfig, line: cli.Line, section: Section) -> None:

        if config.system_packages is not None:
            line.print(cli.dim('installing system packages...'))
            time.sleep(0.25)

            if package_manager == 'apt':
                if apt.install(config.system_packages):
                    section.updated('system packages: installed')
                else:
                    section.unchanged('system packages: up to date')
