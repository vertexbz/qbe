from __future__ import annotations

import os

from .adapter.file import readfile
from .paths import paths


class NiceNames:
    def __init__(self):
        names = readfile(os.path.join(paths.qbe.src, 'nice_names.txt')).split('\n')
        names = map(lambda line: line.strip(), names)
        names = filter(lambda line: len(line) > 0, names)
        self._data = {line.lower(): line for line in names}

    def get(self, name: str) -> str:
        return self._data.get(name.lower(), name)


nice_names = NiceNames()

__all__ = ['nice_names']
