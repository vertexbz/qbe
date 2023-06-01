from __future__ import annotations
import pkgutil
from typing import Type
from .base import BaseHandler, Notification, AnyNotification

HANDLERS: set[BaseHandler.__class__] = set()


def notification_handler(cls):
    if not issubclass(cls, BaseHandler):
        raise ValueError(f'Class {cls} is not a subclass of {BaseHandler}')
    if cls in HANDLERS:
        raise ValueError(f'Name {type(cls)} already registered!')

    HANDLERS.add(cls)

    return cls


def handler(notification: Notification) -> Type[BaseHandler]:
    for h in HANDLERS:
        if isinstance(notification, h.NOTIFICATION):
            return h()

    raise ValueError('Unknown notification type')


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


class NotificationBag:
    def __init__(self):
        self._items: dict[str, Type[Notification]] = {}

    @property
    def items(self):
        return self._items.values()

    def merge(self, bag: NotificationBag):
        for notification in bag.items:
            self.add(notification)

    def add(self, notification: Type[Notification]):
        key = notification.id
        if key in self._items:
            self._items[key].merge(notification)
        else:
            self._items[key] = notification
