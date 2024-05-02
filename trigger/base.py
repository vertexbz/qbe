from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress import ProgressRoot


@dataclass(frozen=True)
class Trigger:
    @classmethod
    @abstractmethod
    def decode(cls, data: dict):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    async def handle(self, progress: ProgressRoot, updatable: Updatable):
        pass
