from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .data_source import ManifestDataSource, build as data_source_build
from .package_type import PackageType
from .providers import ManifestProvides
from .triggers import ManifestTriggers
from ..adapter.dataclass import field


@dataclass(frozen=True)
class Manifest:
    """QBE Package Manifest"""
    name: str
    author: str
    license: str
    provides: list[ManifestProvides]
    homepage: Optional[str] = field(default=None, omitempty=True)
    type: PackageType = PackageType.PACKAGE
    data_source: Optional[ManifestDataSource] = field(default=None, name='data-source', omitempty=True)
    triggers: Optional[ManifestTriggers] = field(default=None, omitempty=True)

    @classmethod
    def decode(cls, data: dict) -> Manifest:
        provides = data.get('provides')
        make_provider = ManifestProvides.decode
        return cls(
            name=data.get('name'),
            author=data.get('author'),
            homepage=data.get('homepage', None),
            license=data.get('license', 'UNKNOWN'),
            type=PackageType(data.get('type', 'package')),
            data_source=data_source_build(data.get('data-source')) if 'data-source' in data else None,
            triggers=ManifestTriggers.decode(data.get('triggers')) if 'triggers' in data else None,
            provides=[make_provider(provides)] if isinstance(provides, dict) else list(map(make_provider, provides))
        )
