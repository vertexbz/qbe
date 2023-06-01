import os
import shutil
from .base import BaseStrategy, Skipped
from . import operation


@operation('link')
class LinkStrategy(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.islink(target) and os.readlink(target) == source:
            raise Skipped('%(target)s already links to %(source)s')

        if os.path.exists(target):
            if os.path.islink(target):
                os.unlink(target)
            else:
                shutil.rmtree(target)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)

        if os.path.islink(target):
            os.remove(target)

        os.symlink(source, target)
        return 'linked %(source)s to %(target)s'
