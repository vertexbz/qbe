import os
import errno
import shutil
from .base import BaseStrategy, Skipped
from . import operation


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise exc


@operation('blueprint')
class BlueprintConfigCommand(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.exists(target):
            raise Skipped('%(target)s already exists')

        os.makedirs(os.path.dirname(target), exist_ok=True)
        copyanything(source, target)
        return 'created %(target)s from template'
