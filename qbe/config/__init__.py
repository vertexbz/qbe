import os
import getpass
from typing import Union
import yaml
from qbe.utils.obj import qrepr, qdict
from ..package_provider import build_dependency
from .paths import ConfigPaths

CONFIG_FILE_NAMES: list[str] = [
    'qbe.yml',
    'qbe.yaml'
]

DEFAULT_CONFIG_FILE_NAME = CONFIG_FILE_NAMES[0]


class Config:
    def __init__(self, **kw) -> None:
        self._user = kw.pop('user', getpass.getuser())
        self._paths = paths = ConfigPaths(**kw.pop('paths', {}))
        self._requires = [build_dependency(dep, paths) for dep in kw.pop('requires', [])]

    __repr__ = qrepr()
    __dict__ = qdict()

    @property
    def is_dirty(self):
        return False

    @property
    def paths(self):
        return self._paths

    @property
    def user(self):
        return self._user

    @property
    def requires(self):
        return self._requires


def load(file: str) -> Config:
    with open(file, 'r', encoding='utf-8') as stream:
        return Config(**yaml.load(stream, Loader=yaml.FullLoader))


def get_config_file_name(directory: str) -> Union[str, None]:
    for file in CONFIG_FILE_NAMES:
        if os.path.isfile(os.path.join(directory, file)):
            return file

    return None
