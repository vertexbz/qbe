from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .root import Paths


class PathsMoonraker:
    def __init__(self, paths: Paths) -> None:
        self._paths = paths

    @property
    def config(self):
        return os.path.join(self._paths.config_root, 'moonraker.conf')

    @property
    def configs(self):
        return os.path.join(self._paths.config_root, 'config')

    @property
    def config_links(self):
        return os.path.join(self._paths.config_root, 'autoload-moonraker')

    @property
    def log(self):
        return os.path.join(self.logs, 'moonraker.log')

    @property
    def logs(self):
        return os.path.join(self._paths.config_root, 'logs')

    @property
    def data(self):
        return self._paths.config_root

    @property
    def theme(self):
        return os.path.join(self.configs, '.theme')

    @property
    def extensions(self):
        return os.path.join(self._paths.packages, 'moonraker', 'moonraker', 'components')
