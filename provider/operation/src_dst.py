from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from ...adapter.dataclass import field, CustomEncode
from ...adapter.yaml import PkgTag
from ...optionable import Optionable


@dataclass
class SrcDst(CustomEncode, Optionable):
    source: Union[str, PkgTag]
    target: str
    only: dict = field(default_factory=dict, omitempty=True)
    unless: dict = field(default_factory=dict, omitempty=True)

    @classmethod
    def decode(cls, data: dict):
        if isinstance(data, dict) and 'source' in data and 'target' in data:
            return cls(
                source=data['source'],
                target=data['target'],
                only=data.get('only', {}),
                unless=data.get('unless', {})
            )

        if isinstance(data, str):
            return cls(source=data, target=data)

        if isinstance(data, PkgTag):
            return cls(source=data, target=data.path)

        if isinstance(data, list) and len(data) == 2 and isinstance(data[0], (str, PkgTag)):
            return cls(source=data[0], target=data[1])

        raise ValueError(f'Invalid config entry {data}')

    def custom_encode(self):
        if not self.only and not self.unless:
            if self.source == self.target or (isinstance(self.source, PkgTag) and self.source.path == self.target):
                return self.source

            return [self.source, self.target]

        if not self.unless:
            return {
                'source': self.source,
                'target': self.target,
                'only': self.only
            }
        if not self.only:
            return {
                'source': self.source,
                'target': self.target,
                'unless': self.unless
            }
        return {
            'source': self.source,
            'target': self.target,
            'only': self.only,
            'unless': self.unless
        }
