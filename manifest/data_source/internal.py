from __future__ import annotations

from dataclasses import dataclass

from .base import ManifestDataSource
from ...adapter.dataclass import field


@dataclass(frozen=True)
class InternalDataSource(ManifestDataSource):
    name: str = field(name='internal')

    @classmethod
    def decode(cls, data: dict) -> ManifestDataSource:
        return cls(
            name=data.get('internal')
        )
