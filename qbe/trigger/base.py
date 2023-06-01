from __future__ import annotations
from typing import TypeVar, Type, Any, TYPE_CHECKING

from qbe.utils.context import build_context
from qbe.utils.obj import qrepr

if TYPE_CHECKING:
    from qbe.package_provider import Dependency
    from qbe.config import Config
    from qbe.package import Section, Package


class sentry:
    pass


class Trigger:
    def __init__(self, data: dict) -> None:
        self.is_quiet = data.pop('quiet', True)
        self._data = data

    def __contains__(self, item: str):
        return item in self._data

    def __getitem__(self, key: str) -> str:
        return self.get(key)

    def get(self, key: str, default: Any = sentry) -> str:
        if key in self._data:
            return self._data[key]

        if default == sentry:
            raise KeyError(f'unknown key {key}')

        return default

    # pylint: disable-next=protected-access
    __repr__ = qrepr(lambda v: v._data)


class BaseTriggerHandler:
    def __init__(
        self,
        config: Config,
        package: Package,
        dependency: Dependency,
        section: Section,
        messages: list[str]
    ):
        self.config = config
        self.package = package
        self.dependency = dependency
        self.section = section
        self.messages = messages

    __repr__ = qrepr()

    def process(self, trigger: Trigger) -> None:
        pass

    @property
    def context(self):
        return build_context(self.config, self.package, self.dependency)


AnyTriggerHandler = TypeVar('AnyTriggerHandler', bound=BaseTriggerHandler)
AnyTriggerHandler = Type[AnyTriggerHandler]
