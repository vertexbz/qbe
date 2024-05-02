from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...lockfile.versioned import Versioned


class DataSource:
    def __init__(self, path: str) -> None:
        self._path = path

    @property
    def path(self) -> str:
        return self._path

    @property
    def has_change_history(self) -> bool:
        return False

    @abstractmethod
    async def refresh(self, lock: Versioned, **kw) -> None:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    async def update(self, lock: Versioned, **kw) -> bool:
        raise NotImplementedError("Not implemented")
