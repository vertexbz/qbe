from __future__ import annotations

import sys

import click

from .formatter import Formatter
from ..lockfile import LockFile
from ..updatable.progress import ProgressRoot


class CliProgress(ProgressRoot):
    def __init__(self, lockfile: LockFile):
        super().__init__(lockfile, Formatter())

    def log(self, message: str) -> None:
        print(message)

    def log_error(self, message: str) -> None:
        print(click.style(message, fg='bright_red'), file=sys.stderr)
