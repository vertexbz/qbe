from __future__ import annotations

from dataclasses import dataclass

from . import data_source
from .base import ManifestDataSource
from ...adapter.dataclass import field


@data_source('local')
@dataclass(frozen=True)
class LocalDataSource(ManifestDataSource):
    path: str = field(name='local')

    @classmethod
    def decode(cls, data: dict) -> ManifestDataSource:
        return cls(
            path=data.get('local')
        )
