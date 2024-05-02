from __future__ import annotations

from typing import TYPE_CHECKING

from . import package
from .base import Package
from ..paths import paths

if TYPE_CHECKING:
    from ..qbefile.dependency.internal import InternalDependency


@package
class InternalPackage(Package):
    DISCRIMINATOR = 'internal'
    _dependency: InternalDependency

    @property
    def package_path(self) -> str:
        return paths.qbe.package(self._dependency.identifier.id)

    @property
    def slug(self) -> str:
        return self.manifest.name or self._dependency.identifier.id

    @property
    def name(self) -> str:
        return self.manifest.name or self._dependency.identifier.id
