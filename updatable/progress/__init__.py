from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from .formatter import LogFormatter
from .package_status import PackageStatus
from .provider import ProviderProgress
from .source import SourcesProgress
from .updatable import UpdatableProgress

if TYPE_CHECKING:
    from .. import Updatable
    from ...trigger import Trigger
    from ...lockfile import LockFile


class ProgressRoot:
    def __init__(self, lockfile: LockFile, formatter: Optional[LogFormatter] = None):
        self._lockfile = lockfile
        self._formatter = formatter or LogFormatter()
        self._triggers: set[tuple[Trigger, Updatable]] = set()
        self._known_updatables: set[str] = set()

        self._installed = 0
        self._updated = 0
        self._removed = 0

    @abstractmethod
    def log(self, message: str) -> None:
        pass

    @abstractmethod
    def log_error(self, message: str) -> None:
        pass

    @property
    def triggers(self) -> set[tuple[Trigger, Updatable]]:
        return self._triggers

    def notify(self, trigger: Trigger, updatable: Updatable) -> None:
        self._triggers.add((trigger, updatable))

    def updatable(self, updatable: Updatable) -> UpdatableProgress:
        self._known_updatables.add(updatable.source.path)
        return UpdatableProgress(self, updatable)

    def mark_installed(self) -> None:
        self._installed = self._installed + 1

    def mark_updated(self) -> None:
        self._updated = self._updated + 1

    def mark_removed(self) -> None:
        self._removed = self._removed + 1

    @property
    def stats_installed(self) -> int:
        return self._installed

    @property
    def stats_updated(self) -> int:
        return self._updated

    @property
    def stats_removed(self) -> int:
        return self._removed

    @property
    def stats_total(self) -> int:
        return len(self._known_updatables)
