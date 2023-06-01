from __future__ import annotations
import os
from enum import Enum
import yaml
from qbe.utils.yaml import Loader as YamlLoader
from qbe.utils.obj import qrepr
from qbe.config import get_config_file_name
from qbe.handler import AnyNotification, NotificationBag
from qbe.trigger import build_triggers
from ..feature_provider import AVAILABLE_PROVIDERS, BaseProvider
from ..package_provider import Dependency


class Status(Enum):
    INSTALLED = 'installed'
    UPDATED = 'updated'
    ERROR = 'error'
    UNCHANGED = 'unchanged'


class Detail:
    @classmethod
    def error(cls, text: str):
        return cls(Status.ERROR, text)

    @classmethod
    def updated(cls, text: str):
        return cls(Status.UPDATED, text)

    @classmethod
    def unchanged(cls, text: str):
        return cls(Status.UNCHANGED, text)

    @classmethod
    def installed(cls, text: str):
        return cls(Status.INSTALLED, text)

    def __init__(self, status: Status, text: str) -> None:
        self.status = status
        self.text = text


class Section:
    def __init__(self, result: Result, name: str) -> None:
        self.name = name
        self.result = result
        self.status = Status.UNCHANGED
        self.details: list[Detail] = []

    def error(self, text: str):
        self.status = Status.ERROR
        self.details.append(Detail.error(text))

    def updated(self, text: str):
        if self.status is Status.UNCHANGED:
            self.status = Status.UPDATED

        self.details.append(Detail.updated(text))

    def installed(self, text: str):
        if self.status is not Status.ERROR:
            self.status = Status.INSTALLED

        self.details.append(Detail.installed(text))

    def notify(self, notification: AnyNotification):
        self.result.notifications.add(notification)

    def unchanged(self, text: str):
        self.details.append(Detail.unchanged(text))

    def is_installed(self):
        return self.status is Status.INSTALLED

    def is_updated(self):
        return self.status is Status.UPDATED

    def is_unchanged(self):
        return self.status is Status.UNCHANGED

    def is_error(self):
        return self.status is Status.ERROR


class Result:
    def __init__(self) -> None:
        self.sections: list[Section] = []
        self.notifications = NotificationBag()

    def section(self, name: str):
        section = Section(self, name)
        self.sections.append(section)
        return section

    @property
    def status(self):
        status = Status.UNCHANGED

        for section in self.sections:
            if section.status is Status.UPDATED and status is Status.UNCHANGED:
                status = Status.UPDATED
            elif section.status is Status.INSTALLED and status is not Status.ERROR:
                status = Status.INSTALLED
            elif section.status is Status.ERROR:
                status = Status.ERROR

        return status


class PackageProvides:
    def __init__(self, data: dict) -> None:
        self._data = {}

        for key, value in data.items():
            provider_cls = AVAILABLE_PROVIDERS.get(key, None)
            if provider_cls is None:
                raise ValueError(f'Unknown config provider {key}')

            config = provider_cls.validate_config(value)
            if config is not None:
                self._data.update({key: config})

    def __contains__(self, item: str):
        return item in self._data

    def __getitem__(self, key: str) -> list[BaseProvider]:
        if key in self._data:
            return self._data[key]

        return []

    # pylint: disable-next=protected-access
    __repr__ = qrepr(lambda v: v._data)

    def get(self, provider: str):
        return self._data.get(provider, None)


class PackageTriggers:
    def __init__(self, data: dict) -> None:
        self.installed = build_triggers(data.pop('installed', []))
        self.updated = build_triggers(data.pop('updated', []))
        self.always = build_triggers(data.pop('always', []))

    __repr__ = qrepr()


class Package:
    def __init__(self, directory: str, data: dict) -> None:
        self.dir = directory

        self.name = data.pop('name')
        self.author = data.pop('author')
        self.license = data.pop('license')
        self.provides = PackageProvides(data.pop('provides'))
        self.triggers = PackageTriggers(data.pop('triggers', {}))

    __repr__ = qrepr()


def load_config(directory: str) -> dict:
    file = get_config_file_name(directory)

    if file is None:
        raise LookupError(f'Package definition missing in {directory}')

    with open(os.path.join(directory, file), 'r', encoding='utf-8') as stream:
        return yaml.load(stream, Loader=YamlLoader)


def load(dependency: Dependency) -> Package:
    return Package(dependency.local, load_config(dependency.qbe_definition))
