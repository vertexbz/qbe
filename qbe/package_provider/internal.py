from __future__ import annotations
import os
from .base import BaseProvider, Dependency, UpdateResult
from . import package_provider
from typing import TYPE_CHECKING

from ..utils.path import qbedir

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class InternalDependency(Dependency):
    def __init__(self, paths: ConfigPaths, **kw) -> None:
        self.id = kw.pop('internal', None)
        super().__init__(paths, self.id, **kw)
        self.qbe_definition = os.path.join(qbedir, 'internal-packages', self.id)


@package_provider('internal')
class Internal(BaseProvider):
    DEPENDENCY = InternalDependency

    def __init__(self, config: InternalDependency) -> None:
        super().__init__(config)

    def update(self) -> UpdateResult:
        return UpdateResult.NONE
