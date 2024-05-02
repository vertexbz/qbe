from __future__ import annotations

import pkgutil
from typing import Type

from .base import BaseMCU

MCU_DISCRIMINATORS: dict[str, Type[BaseMCU]] = {}


def mcu(cls: Type[BaseMCU]):
    if not cls.DISCRIMINATOR:
        raise ValueError('MCU class must provide discriminator')

    if cls.DISCRIMINATOR in MCU_DISCRIMINATORS:
        raise ValueError(f'Type {cls.DISCRIMINATOR} already registered!')
    if not issubclass(cls, BaseMCU):
        raise ValueError(f'Class {cls} is not a subclass of {BaseMCU}')
    MCU_DISCRIMINATORS[cls.DISCRIMINATOR] = cls
    return cls


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


def build(name: str, config: dict) -> BaseMCU:
    for discriminator, cls in MCU_DISCRIMINATORS.items():
        if config.get(discriminator, None) is not None:
            return cls(name, config)

    raise ValueError(f'invalid mcu configuration {config}')
