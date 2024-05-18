from __future__ import annotations

from .changes import Changed, Changes
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

    def update(self):
        data = load_yaml(readfile(self._path))

        added = Changed.new()

        new_packages = [build_dependency(dep) for dep in data.pop('requires', [])]
        new_mcus = [build_mcu(name, mcu) for name, mcu in data.pop('mcus', {}).items()]

        current_packages = {dep.identifier: dep for dep in self._requires}
        for pkg in new_packages:
            if pkg.identifier not in current_packages:
                added.packages.append(pkg)
                self._requires.append(pkg)
            else:
                current_packages.pop(pkg.identifier).update(pkg)
        for pkg in current_packages.values():
            self._requires.remove(pkg)

        current_mcus = {mcu.name: mcu for mcu in self._mcus}
        for mcu in new_mcus:
            if mcu.name not in current_mcus:
                added.mcus.append(mcu)
                self._mcus.append(mcu)
            else:
                current_mcus.pop(mcu.name).update(mcu)
        for mcu in current_mcus.values():
            self._mcus.remove(mcu)

        return Changes(
            added=added,
            removed=Changed(
                packages=list(current_packages.values()),
                mcus=list(current_mcus.values())
            )
        )


def load(file: str) -> QBEFile:
    qbe = QBEFile(file)
    qbe.load()
    return qbe


__all__ = ['QBEFile', 'load']
