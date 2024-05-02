from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .klipper import PathsKlipper
from .klipper_screen import PathsKlipperScreen
from .moonraker import PathsMoonraker
from .qbe import PathsQbe

if TYPE_CHECKING:
    from ..package import Package


class Paths:
    def __init__(self):
        self._qbe = PathsQbe(self)
        self._klipper = PathsKlipper(self)
        self._klipper_screen = PathsKlipperScreen(self)
        self._moonraker = PathsMoonraker(self)

    @property
    def config_root(self):
        return os.path.expanduser('~')

    @property
    def python(self):
        return os.path.join('/', 'usr', 'bin', 'python3')

    @property
    def packages(self):
        return os.path.join('/', 'opt')

    @property
    def venvs(self):
        return os.path.join('/', 'var', 'opt')

    @property
    def firmwares(self):
        return os.path.join(self.config_root, 'firmware')

    @property
    def qbe(self):
        return self._qbe

    @property
    def klipper(self):
        return self._klipper

    @property
    def klipper_screen(self):
        return self._klipper_screen

    @property
    def moonraker(self):
        return self._moonraker

    def package(self, package: Package):
        return str(os.path.join(self.packages, package.slug))

    def venv(self, slug: str):
        return str(os.path.join(self.venvs, slug))
