from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable

from .formatter import Formatter
from ..updatable.progress import ProgressRoot

if TYPE_CHECKING:
    from ..lockfile import LockFile

ANSI_ESCAPE_CODES = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class MoonrakerProgress(ProgressRoot):
    def __init__(self, lockfile: LockFile, logger: Callable[[str], None]):
        super().__init__(lockfile, formatter=Formatter())
        self._logger = logger

    def log(self, message: str) -> None:
        self._logger(ANSI_ESCAPE_CODES.sub('', message))

    def log_error(self, message: str) -> None:
        self._logger(ANSI_ESCAPE_CODES.sub('', message))
