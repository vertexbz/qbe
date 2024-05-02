from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import package
from .base import Package

if TYPE_CHECKING:
    from ..qbefile.dependency.local import LocalDependency


@package
class LocalPackage(Package):
    DISCRIMINATOR = 'local'
    _dependency: LocalDependency

    @property
    def package_path(self) -> str:
        return self._dependency.identifier.id

    @property
    def slug(self) -> str:
        return self.manifest.name or os.path.basename(self._dependency.identifier.id)

    @property
    def name(self) -> str:
        return self.manifest.name or self._dependency.identifier.id
