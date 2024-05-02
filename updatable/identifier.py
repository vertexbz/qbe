from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Identifier:
    type: str
    id: str

    def __str__(self):
        return f'{self.type}#{self.id}'
