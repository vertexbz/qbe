from __future__ import annotations

import pkgutil
from typing import Type

from .base import Trigger

AVAILABLE_TRIGGERS: dict[str, Type[Trigger]] = {}


def trigger(name):
    def register_function_fn(cls):
        if name in AVAILABLE_TRIGGERS:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, Trigger):
            raise ValueError(f'Class {cls} is not a subclass of {Trigger}')
        AVAILABLE_TRIGGERS[name] = cls
        return cls

    return register_function_fn


def build(data: dict) -> Trigger:
    for discriminator, dependency_cls in AVAILABLE_TRIGGERS.items():
        if discriminator in data:
            return dependency_cls.decode(data)


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


def get_trigger_types():
    return AVAILABLE_TRIGGERS.values()
