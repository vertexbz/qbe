from __future__ import annotations

import fcntl


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


def writefile(path: str, data: str) -> int:
    with open(path, 'w', encoding='utf-8') as stream:
        return stream.write(data)


def readfile(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as stream:
        return stream.read()
