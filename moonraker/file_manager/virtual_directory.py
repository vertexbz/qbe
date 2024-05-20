from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

from .virtual_file import VirtualFile
from ...adapter.dataclass import field


@dataclass(frozen=True)
class VirtualDirectory:
    name: str
    files: list[VirtualFile] = field(default_factory=list)

    def file_by_local_path(self, local_path: str) -> Optional[VirtualFile]:
        local_path = os.path.normpath(local_path)
        for file in self.files:
            if file.path == local_path:
                return file

        return None

    def file_by_virtual_path(self, request_file_path: str) -> Optional[VirtualFile]:
        for file in self.files:
            if file.name == request_file_path:
                return file

        return None
