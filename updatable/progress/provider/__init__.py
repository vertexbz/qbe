from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .interface import IProviderProgress
from .sub import ProviderSubProgress
from ..formatter import MessageType

if TYPE_CHECKING:
    from ....trigger import Trigger
    from ....provider.base import Provider
    from ..updatable import UpdatableProgress
    from ....lockfile.provided import ProviderProvided
    from ....lockfile.provided.provider_provided import Entry


class ProviderProgress(IProviderProgress):
    def __init__(self, parent: UpdatableProgress, provider: Provider, provided: ProviderProvided) -> None:
        self._parent = parent
        self._formatter = parent._formatter
        self._provider = provider
        self._provided = provided
        self._changed = False

    @property
    def untouched(self) -> set[Entry]:
        return self._provided.untouched

    @property
    def provided(self) -> set[Entry]:
        return self._provided.all

    def sub(self, name: str, case=False) -> IProviderProgress:
        return ProviderSubProgress(self, name, case=case)

    def __enter__(self) -> IProviderProgress:
        return self

    def __exit__(self, exc, value, tb):
        if exc is None and self._changed:
            self._parent.mark_changed()

    def log(self, message: str, _is_toplevel=True) -> None:
        if _is_toplevel:
            message = self._formatter.format_log(message)
        return self._parent.log(self._formatter.format_provider(self._provider) + message)

    def log_changed(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, _is_toplevel=True, **kw) -> None:
        if input or output:
            self._provided.notice(_path or tuple(), input, output, **kw)

        self._changed = True
        if _is_toplevel:
            message = self._formatter.format_changed(message)
        return self._parent.log(self._formatter.format_provider(self._provider) + message)

    def log_removed(self, message: str, entry: Optional[Entry] = None, typ: MessageType = MessageType.SUCCESS, _is_toplevel=True) -> None:
        if entry:
            self._provided.forget(entry)

        self._changed = True
        if _is_toplevel:
            message = self._formatter.format_removed(message, typ)
        return self._parent.log(self._formatter.format_provider(self._provider) + message)

    def log_unchanged(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, _is_toplevel=True, **kw) -> None:
        if input or output:
            self._provided.notice(_path or tuple(), input, output, **kw)

        if _is_toplevel:
            message = self._formatter.format_unchanged(message)
        return self._parent.log(self._formatter.format_provider(self._provider) + message)

    def forget(self, entry: Optional[Entry]) -> None:
        return self._provided.forget(entry)
    
    def notify(self, trigger: Trigger) -> None:
        return self._parent.notify(trigger)

    def mark_installing(self) -> None:
        return self._parent.mark_installing()
