from __future__ import annotations

from qbe.handler.service_reload import ServiceReload

from .base import BaseTriggerHandler, Trigger
from . import trigger_handler


@trigger_handler('service-reload')
class ServiceReloadHandler(BaseTriggerHandler):
    def process(self, trigger: Trigger) -> None:
        self.section.notify(ServiceReload(
            trigger['service-reload'],
            restart=trigger.get('restart', False),
            daemon_reload=trigger.get('daemon-reload', False)
        ))
