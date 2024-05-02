from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from ..formatter import MessageType

if TYPE_CHECKING:
    from ....trigger import Trigger
    from ....lockfile.provided.provider_provided import Entry


class IProviderProgress:
    @property
    @abstractmethod
    def untouched(self) -> set[Entry]:
        pass

    @property
    @abstractmethod
    def provided(self) -> set[Entry]:
        pass

    @abstractmethod
    def sub(self, name: str, case=False) -> IProviderProgress:
        pass

    @abstractmethod
    def log(self, message: str) -> None:
        pass

    @abstractmethod
    def log_unchanged(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, **kw) -> None:
        pass

    @abstractmethod
    def log_changed(self, message: str, input=None, output=None, _path: Optional[tuple[str, ...]] = None, **kw) -> None:
        pass

    @abstractmethod
    def log_removed(self, message: str, entry: Optional[Entry] = None, typ: MessageType = MessageType.SUCCESS) -> None:
        pass

    @abstractmethod
    def forget(self, entry: Optional[Entry]) -> None:
        pass

    @abstractmethod
    def notify(self, trigger: Trigger) -> None:
        pass

    @abstractmethod
    def mark_installing(self) -> None:
        pass
