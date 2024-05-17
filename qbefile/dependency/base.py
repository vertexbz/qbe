from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import Optional, TYPE_CHECKING

from ...updatable.identifier import Identifier

if TYPE_CHECKING:
    from ...manifest import ManifestDataSource


class Dependency:
    DISCRIMINATOR: Optional[str] = None

    def __init__(self, data: dict):
        self._id = data.pop(self.DISCRIMINATOR)
        self._enabled = data.pop('enabled', True)
        self._options = data.pop('options', {})

    @cached_property
    def identifier(self) -> Identifier:
        return Identifier(self.DISCRIMINATOR, self._id)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def options(self) -> dict:
        return self._options

    @property
    @abstractmethod
    def data_source(self) -> ManifestDataSource:
        pass

    def update(self, source: Dependency) -> None:
        if type(self) is not type(source):
            raise TypeError('Update source dependency must be the same type!')

        self._enabled = source._enabled
        self._options = source._options
