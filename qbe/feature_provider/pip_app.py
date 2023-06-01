from __future__ import annotations
import os
import time
import virtualenv
from qbe.utils.obj import qrepr
import qbe.cli as cli
from qbe.support import Pip
from .base import ConfigOperation
from .mixin.services import ServicesMixin, ServicesConfigMixin
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section


class GitPipAppProviderConfig(ServicesConfigMixin):
    def __init__(self, **kw) -> None:
        ServicesConfigMixin.__init__(self, **kw)
        self.pip_requirements: str = kw.pop('pip-requirements', None)
        self.pip_packages: list[str] = kw.pop('pip-packages', None)
        self.services: list[ConfigOperation] = [ConfigOperation(link) for link in kw.pop('services', [])]

    __repr__ = qrepr()


@feature_provider('pip-app')
class GitPipAppProvider(ServicesMixin):
    @classmethod
    def validate_config(cls, config: dict) -> GitPipAppProviderConfig:
        if not isinstance(config, dict):
            raise ValueError('Invalid configuration for pip-app provider')
        return GitPipAppProviderConfig(**config)

    def process(self, config: GitPipAppProviderConfig, line: cli.Line, section: Section) -> None:
        pkg_dir = self.package.dir
        venv_dir = os.path.join(self.config.paths.venvs, self.package.name)

        if not os.path.isdir(venv_dir):
            line.print(cli.dim('creating virtualenv...'))
            time.sleep(0.25)

            virtualenv.cli_run(['-p', '/usr/bin/python3', venv_dir])
            section.installed('virtualenv: created')
        else:
            section.unchanged('virtualenv: present')

        pip = Pip(venv_dir, cwd=pkg_dir)

        if config.pip_requirements is not None:
            line.print(cli.dim('installing pip requirements...'))
            time.sleep(0.25)

            if pip.install_requirements(self._src_path(config.pip_requirements)):
                section.updated('pip: requirements installed')
            else:
                section.unchanged('pip: requirements up to date')

        if config.pip_packages is not None:
            line.print(cli.dim('installing pip packages...'))
            time.sleep(0.25)

            if pip.install(config.pip_packages):
                section.updated('pip: packages installed')
            else:
                section.unchanged('pip: packages up to date')

        self.process_services(config, line, section)
