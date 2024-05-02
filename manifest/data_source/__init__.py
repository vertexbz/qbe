from __future__ import annotations

import pkgutil
from typing import Type

from .base import ManifestDataSource

AVAILABLE_DATA_SOURCES: dict[str, Type[ManifestDataSource]] = {}


def data_source(name):
    def register_function_fn(cls):
        if name in AVAILABLE_DATA_SOURCES:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, ManifestDataSource):
            raise ValueError(f'Class {cls} is not a subclass of {ManifestDataSource}')
        AVAILABLE_DATA_SOURCES[name] = cls
        return cls

    return register_function_fn


def build(data: dict) -> ManifestDataSource:
    for discriminator, data_source_cls in AVAILABLE_DATA_SOURCES.items():
        if discriminator in data:
            return data_source_cls.decode(data)


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


def get_data_source_types():
    return AVAILABLE_DATA_SOURCES.values()
