from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .root import Paths


class PathsKlipper:
    def __init__(self, paths: Paths) -> None:
        self._paths = paths

    @property
    def pkg(self):
        return os.path.join(self._paths.packages, 'klipper')

    @property
    def serial(self):
        return os.path.join('/', 'run', 'klipper', 'klippy.serial')

    @property
    def sock(self):
        return os.path.join('/', 'run', 'klipper', 'klippy.sock')

    @property
    def config(self):
        return os.path.join(self._paths.config_root, 'klipper.cfg')

    @property
    def configs(self):
        return self._paths.moonraker.configs

    @property
    def config_links(self):
        return os.path.join(self._paths.config_root, 'autoload-klipper')

    @property
    def logs(self):
        return self._paths.moonraker.logs

    @property
    def log(self):
        return os.path.join(self.logs, 'klippy.log')

    @property
    def extensions(self):
        return os.path.join(self.pkg, 'klippy', 'extras')
