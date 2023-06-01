from __future__ import annotations
import os
from typing import TYPE_CHECKING
from qbe.utils.obj import qrepr, qdict
from qbe.utils.path import pop_expand

if TYPE_CHECKING:
    from .moonraker import MoonrakerPaths


class KlipperScreenPaths:
    def __init__(self, moonraker: MoonrakerPaths, packages: str, **kw) -> None:
        self._moonraker = moonraker
        self._log = pop_expand(kw, 'log')
        self._log_name = pop_expand(kw, 'log-name', 'KlipperScreen.log')
        self._config = pop_expand(kw, 'config')
        self._configs = pop_expand(kw, 'configs')
        self._config_links = pop_expand(kw, 'config-links')
        self._config_name = pop_expand(kw, 'config-name', 'KlipperScreen.conf')
        self._pkg = os.path.join(packages, 'klipper-screen')

    __repr__ = qrepr()
    __dict__ = qdict()

    @property
    def log(self):
        return self._log or os.path.join(self._moonraker.logs, self._log_name)

    @property
    def configs(self):
        return self._configs or self._moonraker.configs

    @property
    def config_links(self):
        return self._config_links or self._moonraker.configs

    @property
    def config(self):
        return self._config or os.path.join(self.configs, self._config_name)

    @property
    def pkg(self):
        return self._pkg

    @property
    def themes(self):
        return os.path.join(self._pkg, 'styles')
