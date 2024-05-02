from __future__ import annotations

from typing import TYPE_CHECKING

from ..updatable.data_source.git import TaggedCommit

if TYPE_CHECKING:
    from ..lockfile.versioned import Versioned


class Version:
    def __init__(self, lock: Versioned):
        self._lock = lock

    @property
    def time(self) -> float:
        return self._lock.refresh_time

    @property
    def remote(self) -> str:
        return self._lock.remote_version

    @property
    def local(self) -> str:
        return self._lock.current_version

    @property
    def commits_behind(self) -> list[TaggedCommit]:
        return self._lock.commits_behind
