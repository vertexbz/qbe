from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class VirtualFile:
    path: str
    name: str

    @classmethod
    def decode(cls, path: str) -> VirtualFile:
        path = os.path.normpath(path)
        return cls(path=path, name=os.path.basename(path))
