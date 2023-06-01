import os
from enum import Enum
from typing import TypeVar, Generic
from qbe.utils.obj import qrepr


# class syntax
class UpdateResult(Enum):
    NONE = None
    INSTALLED = 'installed'
    UPDATED = 'updated'
    REMOVED = 'removed'


class Dependency:
    def __init__(self, paths, local, **kw) -> None:
        self.local = os.path.join(paths.packages, local)
        self.qbe_definition = self.local
        self.options = kw.pop('options', {})

    @property
    def name(self):
        return os.path.basename(self.local)

    __repr__ = qrepr()


BR_C = TypeVar('BR_C', bound='Dependency')


class BaseProvider(Generic[BR_C]):
    DEPENDENCY = Dependency

    def __init__(self, config: BR_C) -> None:
        super().__init__()
        self.config = config

    def update(self) -> UpdateResult:
        return UpdateResult.NONE
