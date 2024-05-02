from __future__ import annotations

from abc import abstractmethod
import os
from typing import TYPE_CHECKING, Type, TypeVar, Generic, Union, Optional

from ..adapter.yaml import PkgTag
from ..updatable.data_source.internal import InternalDataSource

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress.provider.interface import IProviderProgress


class Config:
    @classmethod
    @abstractmethod
    def decode(cls, data):
        raise NotImplementedError('Not implemented')


T = TypeVar('T', bound=Config)


class Provider(Generic[T]):
    DISCRIMINATOR: str
    CONFIG: Type[T]

    def __init__(self, updatable: Updatable, config: Optional[T]):
        self._updatable = updatable
        self._config = config

    @abstractmethod
    async def apply(self, progress: IProviderProgress):
        pass

    @abstractmethod
    async def remove(self, progress: IProviderProgress):
        pass

    @property
    @abstractmethod
    def files(self) -> list[str]:
        pass

    def _base_path(self, file: Union[PkgTag, str]):
        source = self._updatable.source
        if isinstance(file, PkgTag) and isinstance(source, InternalDataSource):
            return source.package_path
        return self._updatable.source.path

    def _src_path(self, file: Union[PkgTag, str]):
        return os.path.join(self._base_path(file), str(file))
