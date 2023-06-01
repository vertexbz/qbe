from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...base import BaseProvider


class BaseStrategy:
    def __init__(self, provider: BaseProvider) -> None:
        self.provider = provider

    @property
    def name(self):
        raise NotImplementedError()

    # pylint: disable-next=unused-argument
    def execute(self, source: str, target: str) -> str:
        return 'done'


class StrategyException(Exception): ...


class Skipped(StrategyException):
    def __init__(self, reason: str, *args: object) -> None:
        super().__init__(*args)
        self.reason = reason
