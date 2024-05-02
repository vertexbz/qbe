from __future__ import annotations

from typing import TYPE_CHECKING, Union

from ....confighelper import ConfigError
from ....utils import Sentinel

if TYPE_CHECKING:
    from server import Server


class MockedConfig:
    def __init__(self, server: Server, data: dict):
        self.server = server
        self.data = data

    def get_server(self) -> Server:
        return self.server

    def getint(self, option: str, default: Union[Sentinel, int] = Sentinel.MISSING) -> Union[int, None]:
        if option in self.data:
            value = self.data[option]
            if isinstance(value, int):
                return value

        if default is not Sentinel.MISSING:
            return default

        raise ConfigError(option)
