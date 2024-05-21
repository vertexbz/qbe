from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from getpass import getuser
import os.path
import re
from typing import TYPE_CHECKING, Optional

from .version import Version
from ..paths import paths
from ..nice_names import nice_names

if TYPE_CHECKING:
    from .progress.updatable import UpdatableProgress
    from .data_source.base import DataSource
    from ..lockfile.versioned import Versioned


class UnfinishedUpdateError(Exception):
    pass


class Updatable:
    _source: DataSource

    def __init__(self, lock: Versioned):
        self._lock = lock
        self._version = Version(lock)

    @property
    def source(self) -> DataSource:
        return self._source

    @property
    def version(self) -> Version:
        return self._version

    @property
    def lock(self) -> Versioned:
        return self._lock

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Not implemented")

    @property
    @abstractmethod
    def type(self) -> Optional[str]:
        raise NotImplementedError("Not implemented")

    @property
    @abstractmethod
    def options(self) -> dict:
        raise NotImplementedError("Not implemented")

    @property
    @abstractmethod
    def options_dirty(self) -> bool:
        raise NotImplementedError("Not implemented")

    @property
    @abstractmethod
    def recipie_dirty(self) -> bool:
        raise NotImplementedError("Not implemented")

    @cached_property
    def display_name(self):
        words = []
        for part in re.split('[-_ ]+', self.name):
            words.append(nice_names.get(part.strip().capitalize()))

        name = ' '.join(words)

        updatable_type = self.type
        if updatable_type is None:
            return name

        return f'{updatable_type.capitalize()} :: {name}'

    async def refresh(self, progress: Optional[UpdatableProgress] = None, **kw) -> None:
        await self.source.refresh(self._lock, stdout_callback=progress.log if progress else None)
        self._flush()

    async def update(self, progress: UpdatableProgress, **kw) -> None:
        with progress.sources(self.source) as p:
            installing = not os.path.exists(self.source.path)
            if installing:
                progress.mark_installing()

            if await self.source.update(self._lock, stdout_callback=p.log):
                p.log_changed('installed' if installing else 'updated')
                self._flush()
            else:
                p.log_unchanged('up to date')

    def template_context(self):
        return {
            'user': getuser(),
            'paths': paths,
            'dirs': {
                'pkg': self.source.path
            },
            'options': self.options
        }

    def _flush(self):
        pass
