from __future__ import annotations

from .dependency import build as build_dependency, Dependency
from .mcu import build as build_mcu, BaseMCU
from ..adapter.file import readfile
from ..adapter.yaml import load as load_yaml


class QBEFile:
    def __init__(self, path: str):
        self._path = path
        self._requires: list[Dependency] = []
        self._mcus: list[BaseMCU] = []

    @property
    def path(self) -> str:
        return self._path

    @property
    def requires(self):
        return self._requires

    @property
    def mcus(self):
        return self._mcus

    def load(self):
        data = load_yaml(readfile(self._path))

        self._requires = [build_dependency(dep) for dep in data.pop('requires', [])]
        self._mcus = [build_mcu(name, mcu) for name, mcu in data.pop('mcus', {}).items()]


def load(file: str) -> QBEFile:
    qbe = QBEFile(file)
    qbe.load()
    return qbe


__all__ = ['QBEFile', 'load']
