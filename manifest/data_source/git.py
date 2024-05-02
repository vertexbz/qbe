from __future__ import annotations

from dataclasses import dataclass

from . import data_source
from .base import ManifestDataSource
from ...adapter.dataclass import field


@data_source('git')
@dataclass(frozen=True)
class GitDataSource(ManifestDataSource):
    url: str = field(name='git')
    branch: str = field(default='master', omitempty=True)

    @classmethod
    def decode(cls, data: dict) -> ManifestDataSource:
        return cls(
            url=data.get('git'),
            branch=data.get('branch', 'master')
        )
