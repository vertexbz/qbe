from __future__ import annotations
import os
import sys
from qbe.utils.obj import qrepr, qdict
from .klipper import KlipperPaths
from .klipper_screen import KlipperScreenPaths
from .moonraker import MoonrakerPaths, PRINTER_DATA_KEY
from qbe.utils.path import pop_expand


class ConfigPaths:
    def __init__(self, **kw) -> None:
        self._packages = pop_expand(kw, 'packages')
        self._venvs = pop_expand(kw, 'venvs')
        self._state = pop_expand(kw, 'state')
        printer_data = kw.pop(PRINTER_DATA_KEY, None)
        moonraker = kw.pop('moonraker', {})
        if printer_data is not None and moonraker.get(PRINTER_DATA_KEY, None) is not None:
            raise ValueError(f'only one {PRINTER_DATA_KEY} can be configured')
        if printer_data is not None:
            moonraker[PRINTER_DATA_KEY] = printer_data

        self._moonraker = MoonrakerPaths(self.packages, **moonraker)
        self._klipper = KlipperPaths(self._moonraker, self.packages, **kw.pop('klipper', {}))
        self._klipper_screen = KlipperScreenPaths(self._moonraker, self.packages, **kw.pop('klipper-screen', {}))

    __repr__ = qrepr()

    __dict__ = qdict()

    @property
    def klipper(self):
        return self._klipper

    @property
    def klipper_screen(self):
        return self._klipper_screen

    @property
    def moonraker(self):
        return self._moonraker

    @property
    def qbedir(self):
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    @property
    def qbeenv(self):
        if 'VIRTUAL_ENV' in os.environ:
            return os.environ['VIRTUAL_ENV']

        return os.path.dirname(os.path.dirname(sys.executable))

    @property
    def packages(self):
        if self._packages is not None:
            return self._packages

        if self.qbedir == '/opt/qbe':
            return '/opt'

        if self.qbedir == '/var/opt/qbe':
            return '/opt'

        return os.path.join(os.path.expanduser('~'), 'qbes')

    @property
    def venvs(self):
        if self._venvs is not None:
            return self._venvs

        if self.qbedir == '/opt/qbe':
            return '/var/opt'

        return os.path.expanduser('~')

    @property
    def state(self):
        return self._state or os.path.join(os.path.expanduser('~'), '.qbe')

    @property
    def firmwares(self):
        return os.path.join(self.moonraker.data, 'firmware')
