from __future__ import annotations
import os

from qbe.utils.path import pop_expand
from qbe.utils.obj import qrepr, qdict
from qbe.support import MoonrakerService, services

PRINTER_DATA_KEY = 'data'


class MoonrakerPaths:
    def __init__(self, packages: str, **kw) -> None:
        self._pkg = os.path.join(packages, 'moonraker')
        self._data = pop_expand(kw, PRINTER_DATA_KEY)
        self._logs = pop_expand(kw, 'logs')
        self._configs = pop_expand(kw, 'configs')
        self._config_links = pop_expand(kw, 'config-links')
        self._log = pop_expand(kw, 'log')
        self._config = pop_expand(kw, 'config')

    __repr__ = qrepr()
    __dict__ = qdict()

    @property
    def data(self):
        return self._data or services.moonraker.datapath or MoonrakerService.DEFAULT_DATA

    @property
    def logs(self):
        return self._logs or os.path.join(self.data, 'logs')

    @property
    def configs(self):
        return self._configs or os.path.join(self.data, 'config')

    @property
    def config_links(self):
        return self._config_links or self.configs

    @property
    def theme(self):
        return os.path.join(self.configs, '.theme')

    @property
    def log(self):
        return self._log or services.moonraker.logfile or os.path.join(self.logs, 'moonraker.log')

    @property
    def config(self):
        return self._config or services.moonraker.configfile or os.path.join(self.configs, 'moonraker.conf')

    @property
    def pkg(self):
        return self._pkg

    @property
    def extensions(self):
        return os.path.join(self.pkg, 'moonraker', 'components')
