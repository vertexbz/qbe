from __future__ import annotations
import os
from typing import TYPE_CHECKING
from qbe.utils.obj import qrepr, qdict
from qbe.support import KlipperService, services
from qbe.utils.path import pop_expand

if TYPE_CHECKING:
    from .moonraker import MoonrakerPaths


class KlipperPaths:
    def __init__(self, moonraker: MoonrakerPaths, packages: str, **kw) -> None:
        self._moonraker = moonraker
        self._sock = pop_expand(kw, 'sock')
        self._serial = pop_expand(kw, 'serial')
        self._log = pop_expand(kw, 'log')
        self._config = pop_expand(kw, 'config')
        self._configs = pop_expand(kw, 'configs')
        self._config_links = pop_expand(kw, 'config-links')
        self._pkg = os.path.join(packages, 'klipper')

    __repr__ = qrepr()
    __dict__ = qdict()

    @property
    def sock(self):
        return self._sock or services.klipper.apiserver or KlipperService.DEFAULT_SOCK

    @property
    def serial(self):
        return self._serial or services.klipper.tty or KlipperService.DEFAULT_TTY

    @property
    def log(self):
        return self._log or services.klipper.logfile or os.path.join(self._moonraker.logs, 'klippy.log')

    @property
    def config(self):
        return self._config or services.klipper.configfile or os.path.join(self.configs, 'printer.cfg')

    @property
    def configs(self):
        return self._configs or self._moonraker.configs

    @property
    def config_links(self):
        return self._config_links or self._moonraker.configs

    @property
    def pkg(self):
        return self._pkg

    @property
    def extensions(self):
        return os.path.join(self.pkg, 'klippy', 'extras')
