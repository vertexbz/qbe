from __future__ import annotations
import os.path
import shutil
from enum import Enum
import hashlib
from typing import Union

from qbe.support import Command
from qbe.config.mcu.definition import MCUConfigTemplate
from qbe.utils.file import writefile


class MCUFwStatus(Enum):
    ABSENT = 0
    OUTDATED = 1
    BUILT = 2
    UP_TO_DATE = 3
    NOT_APPLY = -1


def fw_filename(basename: str, options: Union[None, dict] = None, suffix: Union[None, str] = None):
    hash_object = hashlib.sha256(str(options).encode('utf-8'))
    short_hash = hash_object.hexdigest()[:8]

    name = basename

    if suffix is not None:
        name = name + '-' + suffix

    return name + '-' + short_hash + '.bin'


class MCUFirmware:
    def __init__(
        self,
        target_dir: str, name: str, type: str,
        config: MCUConfigTemplate, options: dict,
        source_dir: str
    ):
        self.target_dir = target_dir
        self.config = config
        self.name = name
        self.type = type
        self.options = options
        self.source_dir = source_dir

    @property
    def filename(self):
        return fw_filename(self.name, self.options, self.type)

    @property
    def path(self):
        return os.path.join(self.target_dir, self.filename)

    @property
    def status(self) -> MCUFwStatus:
        if not os.path.exists(self.path):
            return MCUFwStatus.ABSENT

        if self.source_dir is None:
            return MCUFwStatus.OUTDATED

        source_head = os.path.join(self.source_dir, '.git', 'FETCH_HEAD')
        if os.path.getmtime(self.path) < os.path.getmtime(source_head):
            return MCUFwStatus.OUTDATED

        return MCUFwStatus.BUILT

    def render_config(self):
        return self.config.render(self.options)

    def build(self, verbose=False):
        out = os.path.basename(self.source_dir)
        make = Command('/usr/bin/make', cwd=self.source_dir)
        target_config = os.path.join(self.source_dir, '.config')
        target_path = os.path.join(self.source_dir, 'out', out + '.bin')

        make.piped(['clean'])

        writefile(target_config, self.render_config())

        if verbose:
            make.attached([])
        else:
            make.piped([])

        shutil.copyfile(target_path, self.path)

        if os.path.exists(target_config):
            os.unlink(target_config)
