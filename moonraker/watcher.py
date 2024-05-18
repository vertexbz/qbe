from __future__ import annotations

from contextlib import contextmanager
import errno
import os
from typing import TYPE_CHECKING, Callable, Optional, Coroutine

from inotify_simple import INotify, flags, Event

if TYPE_CHECKING:
    from eventloop import EventLoop


class Watcher:
    def __init__(self, event_loop: EventLoop, path: str, callback: Callable[[Event], Optional[Coroutine]]):
        self._event_loop = event_loop
        self._callback = callback
        self._path = path

        self._pause_level = 0
        self._watch_descriptor = None
        self._inotify = INotify(nonblocking=True)
        self._event_loop.add_reader(self._inotify.fileno(), self._handle_inotify_read)

        self._enable()

    def _enable(self):
        if not self._watch_descriptor:
            if os.path.exists(self._path):
                self._watch_descriptor = self._inotify.add_watch(self._path, flags.MODIFY | flags.DELETE_SELF)
            else:
                self._watch_descriptor = self._inotify.add_watch(os.path.dirname(self._path), flags.CREATE)

    def _disable(self):
        if self._watch_descriptor:
            try:
                self._inotify.rm_watch(self._watch_descriptor)
            except OSError as e:
                if e.errno != errno.EINVAL:
                    raise

            self._watch_descriptor = None

    def close(self):
        self._disable()
        self._inotify.close()

    async def handle(self, evt: Event):
        if awaiter := self._callback(evt):
            await awaiter

    @contextmanager
    def paused(self):
        self.pause()
        try:
            yield None
        finally:
            self.resume()

    def pause(self):
        if self._pause_level == 0:
            self._disable()
        self._pause_level += 1

    def resume(self):
        self._pause_level = max(self._pause_level - 1, 0)
        if self._pause_level == 0:
            self._enable()

    def _handle_inotify_read(self) -> None:
        evt: Event
        for evt in self._inotify.read(timeout=0):
            if evt.mask & flags.IGNORED:
                continue

            if evt.wd != self._watch_descriptor:
                continue

            if evt.mask & flags.DELETE_SELF or (evt.mask & flags.CREATE and evt.name == os.path.basename(self._path)):
                self._disable()

                exists = os.path.exists(self._path)
                self._enable()

                if not exists:
                    return

            self._event_loop.delay_callback(0, self.handle, evt)
