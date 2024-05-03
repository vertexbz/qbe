from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Dict, Any

from .mocked_config import MockedConfig
from .progress import MoonrakerProgress
from .utils import format_version
from ..adapter.command import sudo_systemctl_daemon_reload
from ..adapter.dataclass import encode
from ..nice_names import nice_names
from ..trigger.gcode import GCodeTrigger
from ..trigger.service_reload import ServiceReloadTrigger
from ...update_manager.base_deploy import BaseDeploy
from ....utils import pretty_print_time

if TYPE_CHECKING:
    from server import Server
    from ...update_manager.update_manager import CommandHelper
    from ...machine import Machine
    from ...klippy_apis import KlippyAPI as APIComp
    from ..updatable import Updatable
    from ..lockfile import LockFile


class QBEDeployer(BaseDeploy):
    def __init__(self, server: Server, lockfile: LockFile, cmd_helper: CommandHelper, updatable: Updatable) -> None:
        mocked_config = MockedConfig(server, {})
        super().__init__(
            mocked_config,   # type: ignore
            cmd_helper,
            name=updatable.name,
            prefix="QBE Package",
            cfg_hash='fake'
        )
        self._machine: Machine = server.lookup_component("machine")
        self._kapis: APIComp = server.lookup_component('klippy_apis')
        self._lockfile = lockfile
        self._updatable = updatable

    @property
    def display_name(self):
        words = []
        for part in re.split('[-_ ]+', self._updatable.name):
            words.append(nice_names.get(part.strip().capitalize()))

        name = ' '.join(words)

        updatable_type = self._updatable.type
        if updatable_type is None:
            return name

        return f'{updatable_type.capitalize()} :: {name}'

    async def initialize(self):
        return {}

    async def refresh(self) -> None:
        if self._updatable._lock.status.unfinished():
            return
        await self._updatable.refresh()
        self._lockfile.save()

    async def update(self) -> bool:
        self.cmd_helper.notify_update_response(f'Updating {self.display_name}...')

        progress = MoonrakerProgress(self._lockfile, logger=self.notify_status)

        try:
            with progress.updatable(self._updatable) as p:
                await self._updatable.update(p)
        except Exception as e:
            raise self.log_exc(f'Update failed, {e}', False)

        for trig, updatable in progress.triggers:
            if isinstance(trig, GCodeTrigger):
                # TODO if klipper not available queue commands?
                await self._kapis.run_gcode(trig.gcode)
            elif isinstance(trig, ServiceReloadTrigger) and trig.service.lower() in ('moonraker', 'moonraker.service'):
                if trig.daemon_reload:
                    await sudo_systemctl_daemon_reload()

                self.notify_status('Restarting moonraker...')
                self._machine.restart_moonraker_service()
            else:
                await trig.handle(progress, updatable)

        self.notify_status('Saving the lockfile...')
        self._lockfile.save()
        self.notify_status('Update Finished!', is_complete=True)
        return True

    async def recover(self, hard: bool = False, force_dep_update: bool = False) -> None:
        self.notify_status("Recovery not supported", is_complete=True)

    async def rollback(self) -> bool:
        self.notify_status("Rollback not supported", is_complete=True)
        return True

    def get_update_status(self) -> Dict[str, Any]:
        source = self._updatable.source
        local_version = self._updatable.version.local
        remote_version = self._updatable.version.remote
        moonraker_package_type = 'git_repo' if source.has_change_history else 'web'

        return {
            'debug_enabled': self.server.is_debug_enabled(),
            'info_tags': [],

            'configured_type': moonraker_package_type,
            'detected_type': moonraker_package_type,
            'channel': 'stable',
            'channel_invalid': False,
            'is_valid': local_version != '?' and remote_version != '?',
            'is_dirty': self._updatable.options_dirty or self._updatable.recipie_dirty,
            'detached': False,
            'pristine': True,
            'corrupt': self._updatable.lock.status.unfinished(),
            'last_error': self._updatable.lock.last_error or '?',

            'git_messages': [],

            'commits_behind': list(map(encode, self._updatable.version.commits_behind)),
            'commits_behind_count': len(self._updatable.version.commits_behind),

            'full_version_string': format_version(local_version),
            'version': format_version(local_version, short=True),
            'rollback_version': format_version(local_version, short=True),
            'remote_version': format_version(remote_version, short=True),

            'warnings': [
                *(['Options changed, update to apply changes'] if self._updatable.options_dirty else []),
                *(['Recipie changed, update to apply changes'] if self._updatable.recipie_dirty else []),
            ],
            'anomalies': [
                *(['Unfinished update, refresh not available'] if self._updatable.lock.status.unfinished() else []),
            ],

            # TODO: monitor mainsail logic, maybe one day there will be a way to make it better
            **({} if len(self._updatable.version.commits_behind) else {'repo_name': '?', 'owner': '?'})
        }

    def get_persistent_data(self):
        return {
            'last_config_hash': self.cfg_hash,
            'last_refresh_time': self._updatable.version.time
        }

    def get_last_refresh_time(self) -> float:
        return self._updatable.version.time

    def needs_refresh(self, log_remaining_time: bool = False) -> bool:
        next_refresh_time = self._updatable.version.time + self.refresh_interval
        if (remaining_time := int(next_refresh_time - time.time() + .5)) <= 0:
            return True

        if log_remaining_time:
            self.log_info(f"Next refresh in: {pretty_print_time(remaining_time)}")

        return False

    def _save_state(self) -> None:
        pass


# todo removal support?
