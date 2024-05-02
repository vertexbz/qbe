from __future__ import annotations

from dataclasses import make_dataclass, fields, dataclass
from typing import Type

from ..adapter.dataclass import field
from ..provider import providers
from ..provider.base import Config

ManifestProvidesBase = make_dataclass('ManifestProvidesBase', [
    (k.replace('-', '_'), v.CONFIG, field(default=None, name=k, omitempty=True, provider=v))
    for k, v in providers().items()
])


@dataclass
class ManifestProvides(ManifestProvidesBase):
    """Package provides"""
    @classmethod
    def decode(cls, data: dict) -> ManifestProvides:
        class_fields = {f.metadata.get('alias', f.name): (f.name, f.type) for f in fields(cls)}

        values: dict[str, Type[Config]] = {}
        for key, value in data.items():
            if key not in class_fields:
                raise ValueError(f'Invalid provider: {key}')

            field, typ = class_fields[key]

            values[field] = typ.decode(value)

        return cls(**values)


__all__ = ['ManifestProvides']
