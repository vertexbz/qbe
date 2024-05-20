from __future__ import annotations

from asyncio import Handle
import os.path
from types import MethodType
from typing import TYPE_CHECKING, Optional

from inotify_simple import Event

from .blind_proxy import BlindProxy
from .updaters_wrapper import UpdatersWrapper
from .utils import is_mcu_key
from .watcher import Watcher
from .file_manager import hook as hook_file_manager
from ..lockfile import LockFile
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
    from common import WebRequest
    from .file_manager.file_manager import ExtendedFileManager


class QBE:
    def __init__(self, config: ConfigHelper) -> None:
        self._debouncer: Optional[Handle] = None
        self.server = config.get_server()

        # Register handlers
        self.server.register_event_handler('server:klippy_ready', self._klippy_ready)

        # Load config
        qbefile_path = config.get('qbefile', None) or find_in(paths.config_root)

        # Load qbe and lock file
        self.qbefile = load_qbefile(qbefile_path)
        self.qbe_watch = Watcher(self.server.event_loop, self.qbefile.path, self._update_packages)

        lockfile = LockFile.load(for_qbe_file(self.qbefile))
        self.lock_watch = Watcher(self.server.event_loop, lockfile.path, self._update_packages)
        self.lockfile: LockFile = BlindProxy(lockfile, self.lock_watch)

        # Init file manager dirs
        self.init_qbe_views(self.qbefile.path)

        # Wrap updaters
        self.uw = UpdatersWrapper(self.server, self.lockfile)

        # Init updaters
        self.uw.add_updater(QBEPackage(self.lockfile.qbe))

        processed_identifiers = set()
        for dep in self.qbefile.requires:
            processed_identifiers.add(dep.identifier)
            self.uw.add_updater(
                build_package(dep, self.lockfile.requires.always(dep.identifier))
            )

        for mcu_config in self.qbefile.mcus:
            self.uw.add_updater(
                MCU(mcu_config, self.lockfile.mcus.always(mcu_config.name))
            )

        for identifier, lock in self.lockfile.requires.difference(processed_identifiers).items():
            self.uw.add_remover(
                build_package(from_lock(identifier, lock), lock)
            )

    async def _update_packages(self, _: Event):
        if self._debouncer:
            self._debouncer.cancel()
        self._debouncer = self.server.event_loop.delay_callback(2, self._update_packages_debounced)

    async def _update_packages_debounced(self):
        self._debouncer = None
        try:
            updates = self.qbefile.update()
            self.lockfile.update()
        except Exception as e:
            self.server.add_warning(f'Failed reloading qbe/lock file\n{e}')
        else:
            for dep in updates.added.packages:
                updater = self.uw.add_updater(
                    build_package(dep, self.lockfile.requires.always(dep.identifier))
                )
                await updater.initialize()
                await updater.refresh()

            for mcu_config in updates.added.mcus:
                updater = self.uw.add_updater(
                    MCU(mcu_config, self.lockfile.mcus.always(mcu_config.name))
                )
                await updater.initialize()
                await updater.refresh()

            current_removers = {v.package.identifier for v in self.uw.removers}
            for dep in updates.removed.packages:
                if lock := self.lockfile.requires.get(dep.identifier, None):
                    if not lock.is_installed():
                        current_removers.add(dep.identifier)
                        self.lockfile.requires.pop(dep.identifier)
                        continue

                    if dep.identifier in current_removers:
                        current_removers.remove(dep.identifier)

                    updater = self.uw.add_remover(
                        build_package(from_lock(dep.identifier, lock), lock)
                    )
                    await updater.initialize()
                    await updater.refresh()

            for identifier in current_removers:
                if awaiter := self.uw.remove_package(identifier).close():
                    await awaiter

            for mcu in updates.removed.mcus:
                if awaiter := self.uw.remove_mcu(mcu.name).close():
                    await awaiter

            self.uw.notify_update_refreshed()

    async def component_init(self) -> None:
        pass

    async def close(self) -> None:
        self.qbe_watch.close()
        self.lock_watch.close()

    async def _klippy_ready(self) -> None:
        kapis: APIComp = self.server.lookup_component('klippy_apis')

        names = filter(is_mcu_key, await kapis.get_object_list())
        result = await kapis.subscribe_objects({n: None for n in names})

        changed = False
        for name, info in [(k, v) for k, v in result.items() if is_mcu_key(k)]:
            version = info.get('mcu_version', None)
            if version is None:
                continue

            if name == 'mcu':
                name = next(filter(lambda m: m.main, self.qbefile.mcus)).name
            else:
                name = name.removeprefix('mcu ')

            mcu_lock = self.lockfile.mcus.always(name)

            if mcu_lock.current_version != version:
                mcu_lock.current_version = version
                changed = True

        if changed:
            self.lockfile.save()
            self.uw.notify_update_refreshed()

    def init_qbe_views(self, qbefile: str):
        root_contents = os.listdir(paths.config_root)
        file_manager: ExtendedFileManager = self.server.lookup_component('file_manager')

        # Autoload dirs
        for to_link in [d for d in root_contents if d.startswith('autoload-')]:
            dst = os.path.join(paths.config_root, to_link)
            name = ' '.join([w.strip().capitalize() for w in os.path.basename(dst).split('-')])
            file_manager.register_directory('QBE :: ' + name, dst, False)

        # Static config
        file_manager.register_virtual_directory(
            'QBE :: Root Configs',
            [os.path.join(paths.config_root, f) for f in root_contents if f.endswith('.conf') or f.endswith('.cfg')],
            False
        )

        # QBE Config
        file_manager.register_virtual_directory('QBE :: Config', [qbefile], True)


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


def load(config: ConfigHelper) -> QBE:
    # hook FileManager
    hook_file_manager(config)

    # Prepare
    server = config.get_server()
    update_manager: UpdateManager = server.load_component(config, 'update_manager')

    # hook UpdateManager._update_klipper_repo
    update_manager._update_klipper_repo = MethodType(hooked_update_klipper_repo, update_manager)

    # remove default UpdateManager entries
    update_manager.updaters.clear()

    # instantiate the extension
    qbe = QBE(config)

    # hook UpdateManager._handle_full_update_request
    if type_and_api_def := server.moonraker_app.json_rpc.get_method('machine.update.full'):
        cb = update_manager._handle_full_update_request = MethodType(hooked_handle_full_update_request, update_manager)
        object.__setattr__(type_and_api_def[1], 'callback', cb)

    return qbe


__all__ = ['load']
