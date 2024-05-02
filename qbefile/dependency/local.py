from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from . import dependency
from .base import Dependency
from ...manifest.data_source.local import LocalDataSource

if TYPE_CHECKING:
    from ...manifest import ManifestDataSource


@dependency
class LocalDependency(Dependency):
    DISCRIMINATOR = 'local'

    @cached_property
    def data_source(self) -> ManifestDataSource:
        return LocalDataSource(path=self.identifier.id)
