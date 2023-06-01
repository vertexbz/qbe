from __future__ import annotations
from .base import BaseProvider, Dependency, UpdateResult
from . import package_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class LocalDependency(Dependency):
    def __init__(self, paths: ConfigPaths, **kw) -> None:
        self.path = kw.pop('local', None)
        super().__init__(paths, self.path, **kw)


@package_provider('local')
class Local(BaseProvider):
    DEPENDENCY = LocalDependency

    def __init__(self, config: LocalDependency) -> None:
        super().__init__(config)

    def update(self) -> UpdateResult:
        return UpdateResult.NONE
