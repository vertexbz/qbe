from __future__ import annotations

import os.path

from .dependency import DependencyLock
from .lock_dict import LockDict
from .mcu import MCULock
from .qbe import QBELock
from ..adapter.dataclass import encode
from ..adapter.file import readfile, writefile, FileLock
from ..adapter.yaml import load as load_yaml, dump as dump_yaml
from ..updatable.identifier import Identifier

RequiresDict = LockDict[Identifier, DependencyLock]
MCUsDict = LockDict[str, MCULock]


class LockFile:
    def __init__(self, path: str, qbe: QBELock, requires: RequiresDict, mcus: MCUsDict):
        self._path = path
        self._lock = FileLock(path)

        self._qbe = qbe
        self._requires = requires
        self._mcus = mcus

    @property
    def path(self) -> str:
        return self._path

    @property
    def qbe(self) -> QBELock:
        return self._qbe

    @property
    def requires(self) -> RequiresDict:
        return self._requires

    @property
    def mcus(self) -> MCUsDict:
        return self._mcus

    def save(self):
        writefile(self._path, dump_yaml({
            'mcus': self._mcus.to_dict(),
            'qbe': encode(self._qbe),
            'requires': self._requires.to_dict()
        }, None, default_flow_style=False))

    @classmethod
    def _identify_requires_dict(cls, requires: dict) -> dict[Identifier, dict]:
        result = dict()
        for k, v in requires.items():
            typ, id = k.split('#', maxsplit=1)
            result[Identifier(id=id, type=typ)] = v

        return result

    @classmethod
    def load(cls, path: str) -> LockFile:
        requires = LockDict(key_type=Identifier, value_constructor=lambda _: DependencyLock())
        mcus = LockDict(key_type=str, value_constructor=lambda _: MCULock())
        qbe = QBELock()

        try:
            data = load_yaml(readfile(path))

            for k, v in cls._identify_requires_dict(data.pop('requires', {})).items():
                requires[k] = DependencyLock.decode(v)

            for k, v in data.pop('mcus', {}).items():
                mcus[k] = MCULock.decode(v)

            qbe = QBELock.decode(data.pop('qbe', {}))
        except FileNotFoundError:
            pass
        finally:
            result = cls(path, qbe=qbe, mcus=mcus, requires=requires)
            if not os.path.exists(path):
                result.save()

        return result

    def lock(self):
        self._lock.lock()

    def unlock(self):
        self._lock.unlock()
        
    def update(self):
        data = load_yaml(readfile(self.path))
        self._qbe.update(data.pop('qbe', {}))

        current_packages = set(self._requires.keys())
        for id, d in self._identify_requires_dict(data.pop('requires', {})).items():
            if id not in current_packages:
                self._requires[id] = DependencyLock.decode(d)
            else:
                current_packages.remove(id)
                self._requires[id].update(d)
        for id in current_packages:
            del self._requires[id]

        current_mcus = set(self._mcus.keys())
        for name, d in data.pop('mcus', {}).items():
            if name not in self._mcus:
                self._mcus[name] = MCULock.decode(d)
            else:
                current_mcus.remove(name)
                self._mcus[name].update(d)
        for name in current_mcus:
            del self._mcus[name]
