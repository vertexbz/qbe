from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any

from .deployer import QBEDeployer
from ..adapter.dataclass import encode
from ..updatable.data_source.git import TaggedCommit

if TYPE_CHECKING:
    from ..package.base import Package


class QBERemover(QBEDeployer):
    TEXT_PROCESS_STARTING = 'Removing'

    _updatable: Package

    @property
    def package(self) -> Package:
        return self._updatable

    async def _execute(self, progress):
        try:
            with progress.updatable(self._updatable) as p:
                await self._updatable.remove(p)
        except Exception as e:
            raise self.log_exc(f'Removal failed, {e}', False)

    async def _on_complete(self):
        self.notify_status('Removed!', is_complete=True)
        try:
            self._updaters_wrapper.remove_package(self._updatable.identifier)
        except KeyError:
            pass

        if awaiter := self.close():
            await awaiter

        self._updaters_wrapper.notify_update_refreshed()

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
