from __future__ import annotations

from typing import TYPE_CHECKING

from .deployer import QBEDeployer
from .remover import QBERemover
from ..mcu import MCU
from ..package import Package
from ..updatable import Updatable

if TYPE_CHECKING:
    from components.update_manager.update_manager import UpdateManager
    from server import Server
    from ..updatable.identifier import Identifier
    from ..lockfile import LockFile


class UpdatersWrapper:
    def __init__(self, server: Server, lockfile: LockFile):
        self._server = server
        self._update_manager = server.lookup_component('update_manager')
        self._lockfile = lockfile

        self._identifiers_map: dict[Identifier, str] = dict()
        self._mcu_names_map: dict[str, str] = dict()

    @property
    def server(self) -> Server:
        return self._server

    @property
    def lockfile(self) -> LockFile:
        return self._lockfile

    @property
    def update_manager(self) -> UpdateManager:
        return self._update_manager

    @property
    def removers(self) -> list[QBERemover]:
        return list(filter(lambda v: isinstance(v, QBERemover), self._update_manager.updaters.values()))

    def notify_update_refreshed(self) -> None:
        self._update_manager.cmd_helper.notify_update_refreshed()

    def add_updater(self, updatable: Updatable) -> QBEDeployer:
        deployer = QBEDeployer(self, updatable)
        self._update_manager.updaters[deployer.name] = deployer

        if isinstance(updatable, MCU):
            self._mcu_names_map[updatable.name] = deployer.name

        if isinstance(updatable, Package):
            self._identifiers_map[updatable.identifier] = deployer.name

        return deployer

    def add_remover(self, package: Package) -> QBEDeployer:
        deployer = QBERemover(self, package)
        self._update_manager.updaters[deployer.name] = deployer
        self._identifiers_map[package.identifier] = deployer.name
        return deployer

    def remove_mcu(self, name: str) -> QBEDeployer:
        name = self._mcu_names_map.pop(name)
        return self._update_manager.updaters.pop(name)

    def remove_package(self, identifier: Identifier) -> QBEDeployer:
        name = self._identifiers_map.pop(identifier)
        return self._update_manager.updaters.pop(name)
