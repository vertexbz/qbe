from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from . import dependency
from .base import Dependency
from ...manifest.data_source.zip import ZipDataSource

if TYPE_CHECKING:
    from ...manifest import ManifestDataSource


@dependency
class ZipDependency(Dependency):
    DISCRIMINATOR = 'zip'

    @cached_property
    def data_source(self) -> ManifestDataSource:
        return ZipDataSource(url=self.identifier.id)
