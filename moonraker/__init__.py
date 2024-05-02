from __future__ import annotations

import os.path
from types import MethodType
from typing import TYPE_CHECKING

from .deployer import QBEDeployer
from .utils import symlink, register_directory, is_mcu_key
from ..lockfile import load as load_lockfile
from ..lockfile.utils import for_qbe_file
from ..mcu import MCU
from ..package import build as build_package
from ..package.qbe import QBE as QBEPackage
from ..paths import paths
from ..qbefile import load as load_qbefile
from ..qbefile.utils import find_in

if TYPE_CHECKING:
    from confighelper import ConfigHelper
    from components.klippy_apis import KlippyAPI as APIComp
    from components.update_manager.update_manager import UpdateManager


class QBE:
    def __init__(self, config: ConfigHelper) -> None:
        self.updaters = []

        self.server = config.get_server()
        update_manager: UpdateManager = self.server.lookup_component('update_manager')

        self.server.register_event_handler("update_manager:update_refreshed", self._post_refresh)

        qbefile = config.get('qbefile', None)
        qbefile = qbefile if qbefile else find_in(paths.config_root)

        self.qbefile = load_qbefile(qbefile)
        self.lockfile = load_lockfile(for_qbe_file(self.qbefile))
        # todo watch qbe and lock?

        updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, QBEPackage(self.lockfile.qbe))
        update_manager.updaters[updater.display_name] = updater
        self.updaters.append(updater)

        for dep in self.qbefile.requires:
            lock = self.lockfile.requires.always(dep.identifier)
            pkg = build_package(dep, lock)
            updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, pkg)
            update_manager.updaters[updater.display_name] = updater
            self.updaters.append(updater)

        for mcu_config in self.qbefile.mcus:
            lock = self.lockfile.mcus.always(mcu_config.name)
            mcu = MCU(mcu_config, lock)
            updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, mcu)
            update_manager.updaters[updater.display_name] = updater
            self.updaters.append(updater)

        self.lockfile.save()
        self.init_qbe_views(qbefile)

        self.server.register_event_handler('server:klippy_ready', self._klippy_ready)

    async def component_init(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def _klippy_ready(self) -> None:
        kapis: APIComp = self.server.lookup_component('klippy_apis')

        names = filter(is_mcu_key, await kapis.get_object_list())
        result = await kapis.subscribe_objects({n: None for n in names})

        for name, info in [(k, v) for k, v in result.items() if is_mcu_key(k)]:
            version = info.get('mcu_version', None)
            if version is None:
                continue

            if name == 'mcu':
                name = next(filter(lambda m: m.main, self.qbefile.mcus))
            else:
                name = name.removeprefix('mcu ')

            self.lockfile.mcus.always(name).current_version = version

        self.lockfile.save()

    def _post_refresh(self, info: dict):
        self.lockfile.save()

    def hook_post_component_init(self):
        self.lockfile.save()

    def init_qbe_views(self, qbefile: str):
        # Autoload dirs
        views_dir = os.path.join(paths.config_root, '.qbe-views')
        if not os.path.exists(views_dir):
            os.makedirs(views_dir)

        root_contents = os.listdir(paths.config_root)

        for to_link in [d for d in root_contents if d.startswith('autoload-')]:
            dst = symlink(os.path.join(paths.config_root, to_link), views_dir)
            if dst:
                name = ' '.join([w.strip().capitalize() for w in os.path.basename(dst).split('-')])
                register_directory(self.server, 'QBE :: ' + name, dst, False)

        # Static config
        configs_views_dir = os.path.join(views_dir, 'configs')
        if not os.path.exists(configs_views_dir):
            os.makedirs(configs_views_dir)

        for to_link in [f for f in root_contents if f.endswith('.conf') or f.endswith('.cfg')]:
            symlink(os.path.join(paths.config_root, to_link), configs_views_dir)
        register_directory(self.server, 'QBE :: Root Configs', configs_views_dir, False)

        # QBE Config
        config_views_dir = os.path.join(views_dir, 'config')
        if not os.path.exists(config_views_dir):
            os.makedirs(config_views_dir)

        for to_link in [qbefile]:
            symlink(to_link, config_views_dir, hard=True)
        register_directory(self.server, 'QBE :: Config', config_views_dir, True)


async def hooked_update_klipper_repo(*_) -> None:
    pass


def load(config: ConfigHelper) -> QBE:
    server = config.get_server()
    update_manager: UpdateManager = server.load_component(config, 'update_manager')
    update_manager._update_klipper_repo = MethodType(hooked_update_klipper_repo, update_manager)

    # remove default entries
    update_manager.updaters.pop('klipper', None)
    update_manager.updaters.pop('moonraker', None)

    # instantiate the extension
    qbe = QBE(config)

    # hook UpdateManager.component_init
    async def hooked_component_init(self):
        result = await self._original_component_init()
        qbe.hook_post_component_init()
        return result

    update_manager._original_component_init = update_manager.component_init
    update_manager.component_init = MethodType(hooked_component_init, update_manager)

    return qbe


__all__ = ['load']

