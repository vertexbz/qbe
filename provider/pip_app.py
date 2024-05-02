from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
import os
import re
import shutil
from typing import Optional, TYPE_CHECKING, Callable, Union

from . import provider
from .base import Provider
from .operation import SrcDst
from ..adapter.command import pip, shell, sudo_write, sudo_systemctl_service, sudo_rm
from ..adapter.dataclass import field
from ..adapter.file import readfile
from ..adapter.jinja import render
from ..adapter.yaml import PkgTag
from ..paths import paths
from ..trigger.service_reload import ServiceReloadTrigger
from ..updatable.progress.formatter import MessageType

if TYPE_CHECKING:
    from ..updatable.progress.provider.interface import IProviderProgress
    from ..lockfile.provided.provider_provided import Entry


@dataclass
class PipAppConfig:
    setup: bool = field(default=False, omitempty=True)
    pip_requirements: Optional[str] = field(default=None, name='pip-requirements', omitempty=True)
    pip_packages: list[str] = field(default_factory=list, name='pip-packages', omitempty=True)
    services: list[SrcDst] = field(default_factory=list, omitempty=True)

    @classmethod
    def decode(cls, data: dict):
        return cls(
            pip_requirements=data.get('pip-requirements', None),
            pip_packages=data.get('pip-packages', []),
            services=[SrcDst.decode(link) for link in data.get('services', [])]
        )


@provider
class PipAppProvider(Provider[PipAppConfig]):
    DISCRIMINATOR = 'pip-app'
    CONFIG = PipAppConfig

    @cached_property
    def pkg(self):
        return self._updatable.template_context()['dirs']['pkg']

    @cached_property
    def venv(self):
        return self._updatable.template_context()['dirs']['venv']

    async def apply(self, progress: IProviderProgress):
        if self._config:
            with progress.sub('virtualenv') as p:
                if not os.path.isdir(self.venv):
                    p.mark_installing()
                    p.log('creating virtualenv...')

                    await self._virtualenv(p.log)
                    p.log_changed('created', output=self.venv)
                else:
                    p.log_unchanged('present', output=self.venv)

        if self._config and (self._config.setup or self._config.pip_requirements or self._config.pip_packages):
            with progress.sub('pip') as p:
                packages = await self._installed_packages()

                if self._config.setup:
                    with p.sub('setup') as pp:
                        if await self._pip_install_self(packages, pp.log):
                            pp.log_changed('installed', input=self.pkg, output=self.venv)
                        else:
                            pp.log_unchanged('up to date', input=self.pkg, output=self.venv)

                if self._config.pip_packages:
                    with p.sub('packages') as pp:
                        if await self._pip_install_packages(packages, self._config.pip_packages, pp.log):
                            pp.log_changed('installed', output=self.venv)
                        else:
                            pp.log_unchanged('up to date', output=self.venv)

                if self._config.pip_requirements:
                    with p.sub('requirements') as pp:
                        requirements_file = self._src_path(self._config.pip_requirements)
                        if await self._pip_install_requirements(packages, requirements_file, pp.log):
                            pp.log_changed('installed', input=requirements_file, output=self.venv)
                        else:
                            pp.log_unchanged('up to date', input=requirements_file, output=self.venv)

                await self._cleanup_pip(p, progress.untouched)

        if self._config:
            with progress.sub('service') as p:
                for service in self._config.services:
                    with p.sub(service.target, case=True) as pp:
                        source = self._src_path(service.source)
                        content = readfile(source)
                        content = render(content, self._updatable.template_context())
                        target = os.path.join('/etc/systemd/system', service.target)

                        if not os.path.exists(target):
                            await sudo_write(content, target)
                            pp.log_changed('installed', input=source, output=target)
                            pp.notify(ServiceReloadTrigger(os.path.join(service.target)))
                        elif readfile(target) != content:
                            await sudo_write(content, target)
                            pp.log_changed('updated', input=source, output=target)
                            pp.notify(ServiceReloadTrigger(
                                os.path.join(service.target),
                                restart=True, daemon_reload=True
                            ))
                        else:
                            pp.log_unchanged('up to date', input=source, output=target)

                await self._cleanup_services(p, progress.untouched)

    async def remove(self, progress: IProviderProgress):
        with progress.sub('service') as p:
            await self._cleanup_services(p, progress.provided)

        with progress.sub('pip') as p:
            await self._cleanup_pip(p, progress.provided, removing=True)

        virtualenvs = list(filter(lambda e: e.path == ('virtualenv',), progress.provided))
        virtualenv = virtualenvs[0] if len(virtualenvs) > 0 else None
        if virtualenv:
            with progress.sub('virtualenv') as p:
                if os.path.exists(virtualenv.output) and os.path.isdir(virtualenv.output):
                    shutil.rmtree(virtualenv.output, ignore_errors=True)
                p.log_removed('removed', virtualenv)

    @staticmethod
    async def _cleanup_services(progress: IProviderProgress, entries: set[Entry]):
        for entry in list(filter(lambda e: e.path == ('service',), entries)):
            with progress.sub(os.path.basename(entry.output), case=True) as pp:
                await sudo_systemctl_service('stop', os.path.basename(entry.output), stdout_callback=pp.log)
                await sudo_rm(entry.output)
                pp.log_removed('removed', entry)

    @staticmethod
    async def _cleanup_pip(progress: IProviderProgress, entries: set[Entry], removing=False):
        for entry in list(filter(lambda e: e.path[0] == 'pip', entries)):
            with progress.sub(entry.path[1]) as pp:
                if removing:
                    pp.log_removed('removing', entry)
                else:
                    pp.log_removed('retained', entry, typ=MessageType.WARNING)

    @property
    def files(self) -> list[str]:
        if not self._config:
            return []

        return list(filter(None, [
            self._src_path(self._config.pip_requirements) if self._config.pip_requirements else None,
            *[self._src_path(service.source) for service in self._config.services],
        ]))

    # TODO: check versions, handle mixing and changes (removal)
    async def _pip_install_packages(self, current_packages: set[str], packages: list[str], stdout_callback: Callable[[str], None]):
        if all([self._parse_pkg(e)[0] in current_packages for e in packages]):
            return False

        stdout_callback('installing pip packages...')
        command = ' '.join(['install', *packages])
        await pip(command, venv=self.venv, cwd=self.pkg, stdout_callback=stdout_callback)
        return True

    async def _pip_install_self(self, current_packages: set[str], stdout_callback: Callable[[str], None]):
        setup = {}

        setup_file = os.path.join(self.pkg, 'setup.py')
        setuptools = {
            '__file__': setup_file,
            'setup': (lambda **d: setup.update(d)),
            'find_packages': (lambda **d: []),
            'find_namespace_packages': (lambda **d: [])
        }

        content = readfile(setup_file)
        content = re.sub(r'^from setuptools .*$', '', content, flags=re.MULTILINE)
        exec(content, setuptools)

        packages = [self._parse_pkg(e)[0] for e in setup['install_requires']]

        if all([p in current_packages for p in packages]):
            return False

        stdout_callback('installing pip requirements...')

        await pip('install --editable .', venv=self.venv, cwd=self.pkg, stdout_callback=stdout_callback)
        return True

    async def _pip_install_requirements(self, current_packages: set[str], requirements: Union[str, PkgTag], stdout_callback: Callable[[str], None]):
        packages_str = readfile(self._src_path(requirements))
        packages_str = re.sub(r'^--.*|#.*|\s*;.*', '', packages_str, flags=re.MULTILINE)

        packages = filter(lambda s: s.strip() != '', packages_str.split('\n'))
        packages = [self._parse_pkg(e)[0] for e in packages]

        if all([p.lower() in current_packages for p in packages]):
            return False

        stdout_callback('installing pip requirements...')

        command = 'install -r ' + self._src_path(requirements)
        await pip(
            command, venv=self.venv, cwd=self.pkg,
            env={'PATH': os.path.join(self.venv, 'bin') + ':' + os.environ['PATH']},
            stdout_callback=stdout_callback
        )
        return True

    async def _virtualenv(self, stdout_callback: Callable[[str], None]):
        command = f'virtualenv -p {paths.python} {self.venv}'
        await shell(command, cwd=self.pkg, stdout_callback=stdout_callback)

    async def _installed_packages(self) -> set[str]:
        packages = await pip('freeze', venv=self.venv, cwd=self.pkg)

        result = set()
        for entry in packages.split('\n'):
            entry = entry.strip()
            if not entry or entry.startswith('-e'):
                continue

            result.add(self._parse_pkg(entry)[0])

        return result

    @staticmethod
    def _parse_pkg(entry: str) -> tuple[str, Optional[str]]:
        split = re.split(r'[~<>=]=', entry, maxsplit=1)

        name = split[0].strip().lower().replace('_', '-')
        version = split[1].strip() if len(split) > 1 else None

        return name, version
