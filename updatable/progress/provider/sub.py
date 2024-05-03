from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .interface import IProviderProgress
from ..formatter import MessageType

if TYPE_CHECKING:
    from ....trigger import Trigger
    from ....lockfile.provided.provider_provided import Entry


class ProviderSubProgress(IProviderProgress):
    def __init__(self, parent: IProviderProgress, name: str, case=False) -> None:
        self._parent = parent
        self._formatter = parent._formatter
        self._name = name
        self._case = case

    @property
    def untouched(self) -> set[Entry]:
        return self._parent.untouched

    @property
    def provided(self) -> set[Entry]:
        return self._parent.provided

    def sub(self, name: str, case=False) -> IProviderProgress:
        return ProviderSubProgress(self, name, case=case)

    def __enter__(self) -> IProviderProgress:
        return self

    def __exit__(self, exc, value, tb):
        pass

    def log(self, message: str, _is_toplevel=True) -> None:
        if _is_toplevel:
            message = self._formatter.format_log(message)
        return self._parent.log(self._formatter.format_sub(self._name, _is_toplevel, self._case) + message, _is_toplevel=False)

    def log_changed(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, _is_toplevel=True, **kw) -> None:
        if _is_toplevel:
            message = self._formatter.format_changed(message)

        if not self._case:
            _path = (self._name,) + _path if _path else (self._name,)

        return self._parent.log_changed(
            self._formatter.format_sub(self._name, _is_toplevel, self._case) + message,
            input=input, output=output, _path=_path, _is_toplevel=False, **kw
        )

    def log_removed(self, message: str, entry: Optional[Entry] = None, typ: MessageType = MessageType.SUCCESS, _is_toplevel=True) -> None:
        if _is_toplevel:
            message = self._formatter.format_removed(message, typ)

        return self._parent.log_removed(
            self._formatter.format_sub(self._name, _is_toplevel, self._case) + message, entry, _is_toplevel=False
        )

    def log_unchanged(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, _is_toplevel=True, **kw) -> None:
        if _is_toplevel:
            message = self._formatter.format_unchanged(message)

        if not self._case:
            _path = (self._name,) + _path if _path else (self._name,)

        return self._parent.log_unchanged(
            self._formatter.format_sub(self._name, _is_toplevel, self._case) + message,
            input=input, output=output, _path=_path, _is_toplevel=False, **kw
        )

    def forget(self, entry: Optional[Entry]) -> None:
        return self._parent.forget(entry)

    def notify(self, trigger: Trigger) -> None:
        return self._parent.notify(trigger)

    def mark_installing(self) -> None:
        return self._parent.mark_installing()
