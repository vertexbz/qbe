from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING, Type

from .base import Package

if TYPE_CHECKING:
    from ..qbefile.dependency import Dependency
    from ..lockfile.dependency import DependencyLock


PACKAGE_DISCRIMINATORS: dict[str, Type[Package]] = {}


def package(cls: Type[Package]):
    if not cls.DISCRIMINATOR:
        raise ValueError('Package class must provide discriminator')

    if cls.DISCRIMINATOR in PACKAGE_DISCRIMINATORS:
        raise ValueError(f'Type {cls.DISCRIMINATOR} already registered!')
    if not issubclass(cls, Package):
        raise ValueError(f'Class {cls} is not a subclass of {Package}')
    PACKAGE_DISCRIMINATORS[cls.DISCRIMINATOR] = cls
    return cls


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base') and not module.endswith('.qbe'):
        __import__(module)


def build(data: Dependency, lock: DependencyLock) -> Package:
    for discriminator, package_cls in PACKAGE_DISCRIMINATORS.items():
        if discriminator == data.identifier.type:
            return package_cls(data, lock)

    raise ValueError(f'unknown package definition {data}')


__all__ = ['Package', 'build', 'package']
