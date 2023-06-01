from __future__ import annotations
from typing import TypeVar, Generic, Type
from qbe.utils.obj import qrepr


class Notification:
    @property
    def id(self) -> str:
        raise NotImplementedError()

    def merge(self, other: Notification):
        pass

    __repr__ = qrepr()


AnyNotification = TypeVar('AnyNotification', bound=Notification)
AnyNotification = Type[AnyNotification]

BH_N = TypeVar('BH_N', bound='Notification')


class BaseHandler(Generic[BH_N]):
    NOTIFICATION: BH_N.__class__ = Notification

    def handle(self, notification: BH_N) -> None:
        pass
