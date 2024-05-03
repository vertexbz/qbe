from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import trigger
from .base import Trigger
from ..adapter.command import sudo_systemctl_daemon_reload, sudo_systemctl_service, CommandError
from ..adapter.dataclass import field

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress import ProgressRoot


@trigger('service-reload')
@dataclass(frozen=True)
class ServiceReloadTrigger(Trigger):
    service: str = field(name='service-reload')
    restart: bool = field(default=False, omitempty=True)
    daemon_reload: bool = field(default=False, name='daemon-reload', omitempty=True)

    @classmethod
    def decode(cls, data: dict):
        return cls(
            service=data.get('service-reload'),
            restart=data.get('restart', False),
            daemon_reload=data.get('daemon-reload', False)
        )

    async def handle(self, progress: ProgressRoot, updatable: Updatable):
        if self.daemon_reload:
            await sudo_systemctl_daemon_reload()

        try:
            await self._handle()
        except CommandError as e:
            progress.log_error(f'Service {self.service} reload failed: {e}')

    async def _handle(self):
        if self.restart:
            await sudo_systemctl_service('restart', self.service)

        try:
            await sudo_systemctl_service('reload', self.service)
        except CommandError:
            await sudo_systemctl_service('restart', self.service)

    @classmethod
    def dedupe(cls, triggers: set[tuple[Trigger, Updatable]]) -> set[tuple[Trigger, Updatable]]:
        result: set[tuple[Trigger, Updatable]] = set()
        reloads: dict[str, ServiceReloadTrigger] = dict()
        updatables: dict[str, Updatable] = dict()

        for trigger, updatable in triggers:
            if not isinstance(trigger, ServiceReloadTrigger):
                result.add((trigger, updatable))
                continue

            if trigger.service not in reloads:
                reloads[trigger.service] = trigger
                updatables[trigger.service] = updatable
            elif (old := reloads[trigger.service]) != trigger:
                reloads[trigger.service] = ServiceReloadTrigger(
                    service=trigger.service,
                    restart=old.restart or trigger.restart,
                    daemon_reload=old.daemon_reload or trigger.daemon_reload
                )

        for trigger in reloads.values():
            result.add((trigger, updatables[trigger.service]))

        return result
