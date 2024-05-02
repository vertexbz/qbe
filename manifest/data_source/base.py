from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManifestDataSource:
    """Package data source"""
    @classmethod
    def decode(cls, data: dict) -> ManifestDataSource:
        raise NotImplementedError('Subclasses must implement')
