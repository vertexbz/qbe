from __future__ import annotations

import pkgutil
from typing import Type

from .base import Provider

AVAILABLE_PROVIDERS: dict[str, Type[Provider]] = {}


def provider(cls):
    if not issubclass(cls, Provider):
        raise ValueError(f'Class {cls} is not a subclass of {Provider}')

    name = cls.DISCRIMINATOR
    if name in AVAILABLE_PROVIDERS:
        raise ValueError(f'Name {name} already registered!')
    AVAILABLE_PROVIDERS[name] = cls
    return cls


def providers():
    return AVAILABLE_PROVIDERS.copy()


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)

__all__ = ['provider', 'providers']
