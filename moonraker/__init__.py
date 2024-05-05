from __future__ import annotations

import os.path
from types import MethodType
from typing import TYPE_CHECKING, Any

from .deployer import QBEDeployer
from .remover import QBERemover
from .utils import symlink, register_directory, is_mcu_key, NoLowerString
from ..lockfile import load as load_lockfile
from ..lockfile.utils import for_qbe_file
from ..mcu import MCU
from ..package import build as build_package
from ..package.qbe import QBE as QBEPackage
from ..paths import paths
from ..qbefile import load as load_qbefile
from ..qbefile.dependency import from_lock
from ..qbefile.utils import find_in

if TYPE_CHECKING:
    from confighelper import ConfigHelper
    from components.klippy_apis import KlippyAPI as APIComp
    from components.update_manager.update_manager import UpdateManager
    from components.file_manager.file_manager import FileManager
    from common import WebRequest


class QBE:
    def __init__(self, config: ConfigHelper) -> None:
        self.server = config.get_server()
        update_manager: UpdateManager = self.server.lookup_component('update_manager')

        self.server.register_event_handler("update_manager:update_refreshed", self._post_refresh)

        qbefile = config.get('qbefile', None)
        qbefile = qbefile if qbefile else find_in(paths.config_root)

        self.qbefile = load_qbefile(qbefile)
        self.lockfile = load_lockfile(for_qbe_file(self.qbefile))

        updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, QBEPackage(self.lockfile.qbe))
        update_manager.updaters[updater.display_name] = updater

        processed_identifiers = set()
        for dep in self.qbefile.requires:
            processed_identifiers.add(dep.identifier)
            lock = self.lockfile.requires.always(dep.identifier)
            pkg = build_package(dep, lock)
            updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, pkg)
            update_manager.updaters[updater.display_name] = updater

        for mcu_config in self.qbefile.mcus:
            lock = self.lockfile.mcus.always(mcu_config.name)
            mcu = MCU(mcu_config, lock)
            updater = QBEDeployer(self.server, self.lockfile, update_manager.cmd_helper, mcu)
            update_manager.updaters[updater.display_name] = updater

        for identifier, lock in self.lockfile.requires.difference(processed_identifiers).items():
            pkg = build_package(from_lock(identifier, lock), lock)
            updater = QBERemover(self.server, self.lockfile, update_manager.cmd_helper, pkg)
            update_manager.updaters[updater.display_name] = updater

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
                name = next(filter(lambda m: m.main, self.qbefile.mcus)).name
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


async def hooked_handle_full_update_request(self: UpdateManager, web_request: WebRequest) -> str:
    async with self.cmd_request_lock:
        app_name = ""
        self.cmd_helper.set_update_info('full', id(web_request))
        self.cmd_helper.notify_update_response("Preparing full software update...")
        try:
            # Perform system updates
            if 'system' in self.updaters:
                app_name = 'system'
                await self.updaters['system'].update()

            # Update clients
            for name, updater in self.updaters.items():
                app_name = name
                await updater.update()

            self.cmd_helper.set_full_complete(True)
            self.cmd_helper.notify_update_response("Full Update Complete", is_complete=True)
        except Exception as e:
            self.cmd_helper.set_full_complete(True)
            self.cmd_helper.notify_update_response(f"Error updating {app_name}: {e}", is_complete=True)
        finally:
            self.cmd_helper.clear_update_info()
        return "ok"


def hooked_parse_upload_args(self, upload_args: dict[str, Any]) -> dict[str, Any]:
    if 'root' in upload_args and upload_args['root'].startswith('QBE :: '):
        upload_args['root'] = NoLowerString(upload_args['root'])

    return self._original_parse_upload_args(upload_args)


def load(config: ConfigHelper) -> QBE:
    server = config.get_server()
    file_manager: FileManager = server.load_component(config, 'file_manager')
    update_manager: UpdateManager = server.load_component(config, 'update_manager')

    # hook UpdateManager._update_klipper_repo
    update_manager._update_klipper_repo = MethodType(hooked_update_klipper_repo, update_manager)

    # remove default UpdateManager entries
    update_manager.updaters.clear()

    # instantiate the extension
    qbe = QBE(config)

    # hook UpdateManager.component_init
    async def hooked_component_init(self):
        result = await self._original_component_init()
        qbe.hook_post_component_init()
        return result

    update_manager._original_component_init = update_manager.component_init
    update_manager.component_init = MethodType(hooked_component_init, update_manager)

    # hook UpdateManager._handle_full_update_request
    if type_and_api_def := update_manager.server.moonraker_app.json_rpc.get_method('machine.update.full'):
        cb = update_manager._handle_full_update_request = MethodType(hooked_handle_full_update_request, update_manager)
        object.__setattr__(type_and_api_def[1], 'callback', cb)

    # hook FileManager._parse_upload_args
    file_manager._original_parse_upload_args = file_manager._parse_upload_args
    file_manager._parse_upload_args = MethodType(hooked_parse_upload_args, file_manager)

    return qbe


__all__ = ['load']

