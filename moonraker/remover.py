from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any

from .deployer import QBEDeployer
from ..adapter.dataclass import encode
from ..updatable.data_source.git import TaggedCommit

if TYPE_CHECKING:
    from server import Server
    from ...update_manager.update_manager import CommandHelper
    from ..package.base import Package
    from ..lockfile import LockFile


class QBERemover(QBEDeployer):
    TEXT_PROCESS_STARTING = 'Removing'

    _updatable: Package

    def __init__(self, server: Server, lockfile: LockFile, cmd_helper: CommandHelper, updatable: Package) -> None:
        super().__init__(server, lockfile, cmd_helper, updatable)

    async def _execute(self, progress):
        try:
            with progress.updatable(self._updatable) as p:
                await self._updatable.remove(p)
        except Exception as e:
            raise self.log_exc(f'Removal failed, {e}', False)

    async def _on_complete(self):
        self.notify_status('Removed!', is_complete=True)
        self.cmd_helper.get_updaters().pop(self.display_name, None)
        if awaiter := self.close():
            await awaiter
        self.cmd_helper.notify_update_refreshed()

    def get_update_status(self) -> Dict[str, Any]:
        return {
            **super().get_update_status(),
            'is_dirty': True,
            'detached': False,
            'corrupt': False,
            'pristine': True,

            'commits_behind': [
                encode(TaggedCommit(
                    sha='removing', author='QBE', date='now', tag=None,
                    subject='Removal', message='Package will be removed'
                ))
            ],
            'commits_behind_count': 1,
            'remote_version': '?',

            'warnings': [],
            'anomalies': [
                'Will be removed'
            ]
        }
