from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_source import DataSource
    from . import UpdatableProgress


class SourcesProgress:
    def __init__(self, parent: UpdatableProgress, data_source: DataSource) -> None:
        self._parent = parent
        self._formatter = parent._formatter
        self._data_source = data_source
        self._changed = False

    def __enter__(self) -> SourcesProgress:
        return self

    def __exit__(self, exc, value, tb):
        if exc is None and self._changed:
            self._parent.mark_changed()

    def log(self, message: str) -> None:
        return self._parent.log(self._formatter.format_data_source(self._data_source) + self._formatter.format_log(message), _is_toplevel=False)

    def log_changed(self, message: str) -> None:
        self._changed = True
        return self._parent.log(self._formatter.format_data_source(self._data_source) + self._formatter.format_changed(message), _is_toplevel=False)

    def log_removed(self, message: str) -> None:
        self._changed = True
        return self._parent.log(self._formatter.format_data_source(self._data_source) + self._formatter.format_removed(message), _is_toplevel=False)

    def log_unchanged(self, message: str) -> None:
        return self._parent.log(self._formatter.format_data_source(self._data_source) + self._formatter.format_unchanged(message), _is_toplevel=False)
