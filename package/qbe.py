from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from ..adapter.command import shell
from ..paths import paths
from ..provider.pip_app import PipAppProvider, PipAppConfig
from ..trigger.service_reload import ServiceReloadTrigger
from ..updatable import Updatable
from ..updatable.data_source.git import GitDataSource

if TYPE_CHECKING:
    from updatable.progress import UpdatableProgress
    from ..lockfile.qbe import QBELock


class QBE(Updatable):
    def __init__(self, lock: QBELock):
        super().__init__(lock)
        self._source = GitDataSource(paths.qbe.src)

    @property
    def name(self) -> str:
        return 'QBE'

    @property
    def type(self) -> Optional[str]:
        return None

    @property
    def options(self) -> dict:
        return {}

    @property
    def options_dirty(self) -> bool:
        return False

    @property
    def recipie_dirty(self) -> bool:
        return False  # never dirty, hardcoded

    async def update(self, progress: UpdatableProgress, **kw) -> None:
        await super().update(progress, **kw)  # pull

        provider = PipAppProvider(self, PipAppConfig(setup=True))
        with progress.provider(provider) as p:
            await provider.apply(p)

        if progress.installed:
            python = os.path.join(provider.venv, 'bin', 'python')
            pkg_dir = await shell(python + ' -c \'import site; print(site.getsitepackages()[0])\'', strip=True)
            await shell(f'ln -sf {provider.pkg} {pkg_dir}/qbe')

        if progress.updated or progress.installed:
            progress.notify(ServiceReloadTrigger(service='moonraker', daemon_reload=False, restart=True))

        self.lock.current_version = self.lock.remote_version
        self.lock.commits_behind = []

    def template_context(self):
        sup = super().template_context()
        return {
            **sup,
            'dirs': {
                **sup['dirs'],
                'venv': paths.qbe.venv
            },
        }