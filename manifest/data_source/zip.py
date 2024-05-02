from __future__ import annotations

from dataclasses import dataclass

from . import data_source
from .base import ManifestDataSource
from ...adapter.dataclass import field


@data_source('zip')
@dataclass(frozen=True)
class ZipDataSource(ManifestDataSource):
    url: str = field(name='zip')

    @classmethod
    def decode(cls, data: dict) -> ManifestDataSource:
        return cls(
            url=data.get('zip')
        )
