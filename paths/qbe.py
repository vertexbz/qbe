from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .root import Paths


class PathsQbe:
    def __init__(self, paths: Paths) -> None:
        self._paths = paths

    @property
    def src(self):
        return os.path.join(self._paths.packages, 'qbe')

    @property
    def venv(self):
        return os.path.join(self._paths.venvs, 'qbe')

    @property
    def packages(self):
        return os.path.join(self.src, 'internal-packages')

    @property
    def mcus(self):
        return os.path.join(self.src, 'mcus')

    def package(self, package_name: str) -> str:
        return os.path.join(self.packages, package_name)

    def mcu_preset(self, preset_name: str) -> str:
        return os.path.join(self.mcus, preset_name)
