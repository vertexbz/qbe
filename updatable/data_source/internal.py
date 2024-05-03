from __future__ import annotations

from typing import TYPE_CHECKING

from .base import DataSource

if TYPE_CHECKING:
    from ...lockfile.versioned import Versioned


class InternalDataSource(DataSource):
    def __init__(self, package_path: str, data_source: DataSource) -> None:
        super().__init__(data_source.path)
        self._data_source = data_source
        self._package_path = package_path

    @property
    def package_path(self) -> str:
        return self._package_path

    @property
    def has_change_history(self) -> bool:
        return self._data_source.has_change_history

    async def refresh(self, lock: Versioned, **kw) -> None:
        return await self._data_source.refresh(lock, **kw)

    async def update(self, lock: Versioned, **kw) -> bool:
        return await self._data_source.update(lock, **kw)
