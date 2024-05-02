from __future__ import annotations

from typing import TYPE_CHECKING

from . import dependency
from .base import Dependency
from ...manifest.data_source.internal import InternalDataSource

if TYPE_CHECKING:
    from manifest import ManifestDataSource


@dependency
class InternalDependency(Dependency):
    DISCRIMINATOR = 'internal'

    @property
    def data_source(self) -> ManifestDataSource:
        return InternalDataSource(name=self.identifier.id)
