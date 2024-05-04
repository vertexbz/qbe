from __future__ import annotations

import fcntl
import os.path

from .dependency import DependencyLock
from .lock_dict import LockDict
from .mcu import MCULock
from .qbe import QBELock
from ..adapter.dataclass import encode
from ..adapter.file import readfile, writefile
from ..adapter.yaml import load as load_yaml, dump as dump_yaml
from ..updatable.identifier import Identifier


def new_mcu_dict(self: LockFile):
    return LockDict(
        self, key_type=str,
        value_constructor=lambda _: MCULock(),
    )


def new_requires_dict(self: LockFile):
    return LockDict(
        self, key_type=Identifier,
        value_constructor=lambda _: DependencyLock(),
    )


class LockFile:
    def __init__(self, path: str):
        self._path = path
        self._lock = FileLock(path)

        self._progress: list = []
        self._mcus: LockDict[str, MCULock] = new_mcu_dict(self)
        self._qbe = QBELock.decode({})
        self._requires: LockDict[Identifier, DependencyLock] = new_requires_dict(self)

    @property
    def mcus(self) -> LockDict[str, MCULock]:
        return self._mcus

    @property
    def qbe(self) -> QBELock:
        return self._qbe

    @property
    def requires(self) -> LockDict[Identifier, DependencyLock]:
        return self._requires

    def save(self):
        writefile(self._path, dump_yaml({
            'mcus': self._mcus.to_dict(),
            'qbe': encode(self._qbe),
            'requires': self._requires.to_dict()
        }, None, default_flow_style=False))

    def load(self):
        if not os.path.exists(self._path):
            self.save()
            return

        data = load_yaml(readfile(self._path))

        self._progress = [v for v in data.pop('progress', [])]

        mcus = new_mcu_dict(self)
        for k, v in data.pop('mcus', {}).items():
            mcus[k] = MCULock.decode(v)
        self._mcus = mcus

        self._qbe = QBELock.decode(data.pop('qbe', {}))

        requires = new_requires_dict(self)
        for k, v in data.pop('requires', {}).items():
            type, id = k.split('#', maxsplit=1)
            requires[Identifier(id=id, type=type)] = DependencyLock.decode(v)
        self._requires = requires

    def lock(self):
        self._lock.lock()

    def unlock(self):
        self._lock.unlock()


def load(file: str) -> LockFile:
    lock = LockFile(file)
    lock.load()
    return lock


class FileLock:
    def __init__(self, path: str):
        self._path = path
        self._count = 0
        self._fd = None

    def lock(self):
        if not self._fd:
            self._fd = open(self._path)
            try:
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                raise RuntimeError('Other operation in progress')

        self._count += 1

    def unlock(self):
        self._count -= 1
        if self._count > 0:
            return

        self._count = 0
        if self._fd:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            self._fd.close()
            self._fd = None
