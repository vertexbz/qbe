from __future__ import annotations

import click

from .color import name_color
from ..provider.base import Provider
from ..updatable import Updatable
from ..updatable.data_source.base import DataSource
from ..updatable.progress.formatter import LogFormatter, MessageType


class Formatter(LogFormatter):
    def __init__(self, is_mcu=False):
        self._is_mcu = is_mcu

    def format_updatable(self, updatable: Updatable) -> str:
        color = name_color(updatable.name)
        if self._is_mcu:
            return f'[MCU {click.style(updatable.name, fg=color)}]'

        return click.style(f'[{updatable.name}]', fg=color)

    def format_provider(self, provider: Provider) -> str:
        return click.style(f'[{provider.DISCRIMINATOR}]', fg='bright_blue')

    def format_data_source(self, data_source: DataSource) -> str:
        return click.style(f'[package]', fg='bright_blue')

    def format_sub(self, sub: str, toplevel: bool, case: bool) -> str:
        if case:
            sub = click.style(sub, fg='cyan')
            return f' {sub}'
        return click.style(f'[{sub}]', fg='bright_cyan')

    def format_log(self, message: str) -> str:
        return ' ' + click.style(message, dim=True)

    def format_changed(self, message: str) -> str:
        return ' ' + click.style(message, fg='bright_green')

    def format_removed(self, message: str, typ: MessageType = MessageType.SUCCESS) -> str:
        return ' ' + click.style(message, fg=self.color_for_type(typ))

    @staticmethod
    def color_for_type(typ: MessageType) -> str:
        if typ == MessageType.SUCCESS:
            return 'green'
        elif typ == MessageType.WARNING:
            return 'yellow'
        elif typ == MessageType.ERROR:
            return 'red'
        return 'white'
