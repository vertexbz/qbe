from __future__ import annotations

import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...provider.base import Provider
    from ..data_source import DataSource
    from .. import Updatable


class MessageType(enum.Enum):
    INFO = 'INFO'
    SUCCESS = 'SUCCESS'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class LogFormatter:

    def format_updatable(self, updatable: Updatable) -> str:
        return f'{updatable.name}: '

    def format_provider(self, provider: Provider) -> str:
        return f'{provider.DISCRIMINATOR}: '

    def format_data_source(self, data_source: DataSource) -> str:
        return f'package: '

    def format_sub(self, sub: str, toplevel: bool, case: bool) -> str:
        if case:
            return f' {sub}'
        return f'{sub}: '

    def format_log(self, message: str) -> str:
        return ' ' + message

    def format_changed(self, message: str) -> str:
        return ' ' + message

    def format_removed(self, message: str, typ: MessageType = MessageType.SUCCESS) -> str:
        return ' ' + message

    def format_unchanged(self, message: str) -> str:
        return ' ' + message
