from __future__ import annotations
from qbe.handler import Notification, BaseHandler, notification_handler
from qbe.support import find, systemctl

EXT = '.service'


class ServiceReload(Notification):
    def __init__(self, service: str, **kw):
        self.service = service if service.endswith(EXT) else service + EXT
        self.restart = kw.pop('restart', False)
        self.daemon_reload = kw.pop('daemon_reload', False)

    @property
    def id(self) -> str:
        return type(self).__name__ + ':' + self.service

    def merge(self, other: ServiceReload):
        self.restart = self.restart or other.restart
        self.daemon_reload = self.daemon_reload or other.daemon_reload

    def __str__(self):
        return 'reload service: ' + self.service


@notification_handler
class ServiceReloadHandler(BaseHandler):
    NOTIFICATION = ServiceReload

    def handle(self, notification: ServiceReload) -> None:
        if notification.daemon_reload:
            systemctl.daemon_reload()

        systemctl.enable(notification.service)
        if notification.restart:
            systemctl.restart(notification.service)
        else:
            try:
                systemctl.reload(notification.service)
            except:
                systemctl.restart(notification.service)
