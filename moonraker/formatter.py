from __future__ import annotations

from typing import TYPE_CHECKING

from ..updatable.progress.formatter import LogFormatter

if TYPE_CHECKING:
    from ..updatable import Updatable


class Formatter(LogFormatter):
    def format_updatable(self, updatable: Updatable) -> str:
        return ''
