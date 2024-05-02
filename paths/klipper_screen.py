from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .root import Paths


class PathsKlipperScreen:
    def __init__(self, paths: Paths) -> None:
        self._paths = paths

    @property
    def config(self):
        return os.path.join(self._paths.config_root, 'screen.conf')

    @property
    def configs(self):
        return self._paths.moonraker.configs

    @property
    def config_links(self):
        return os.path.join(self._paths.config_root, 'autoload-screen')

    @property
    def log(self):
        return os.path.join(self._paths.moonraker.logs, 'klipper-screen.log')

    @property
    def themes(self):
        return os.path.join(self._paths.packages, 'klipper-screen', 'styles')
