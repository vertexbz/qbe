from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Callable, TypeVar, Generic

from .watcher import Watcher
from ..lockfile import LockFile

Proxied = TypeVar('Proxied', bound=LockFile)


class BlindProxy(Generic[Proxied], Proxied if TYPE_CHECKING else object):
    def __init__(self, target: Proxied, watcher: Watcher):
        self._target = target
        self._watcher = watcher

    def __getattribute__(self, item: str):
        original = super().__getattribute__('_target').__getattribute__(item)

        try:
            hooked = super().__getattribute__(f'hook_{item}')
        except AttributeError:
            return original
        else:
            return partial(hooked, original)

    def hook_save(self, original: Callable[[], None]) -> None:
        watcher: Watcher = super().__getattribute__('_watcher')
        with watcher.paused():
            return original()
