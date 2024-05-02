from __future__ import annotations

import pkgutil
from typing import Type, TYPE_CHECKING

from .base import Dependency

if TYPE_CHECKING:
    from ...updatable.identifier import Identifier
    from ...lockfile.dependency import DependencyLock

DEPENDENCY_DISCRIMINATORS: dict[str, Type[Dependency]] = {}


def dependency(cls: Type[Dependency]):
    if not cls.DISCRIMINATOR:
        raise ValueError('Dependency class must provide discriminator')

    if cls.DISCRIMINATOR in DEPENDENCY_DISCRIMINATORS:
        raise ValueError(f'Type {cls.DISCRIMINATOR} already registered!')
    if not issubclass(cls, Dependency):
        raise ValueError(f'Class {cls} is not a subclass of {Dependency}')
    DEPENDENCY_DISCRIMINATORS[cls.DISCRIMINATOR] = cls
    return cls


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base') and not module.endswith('.local'):
        __import__(module)

__import__(__name__ + '.local')


def build(data: dict) -> Dependency:
    for discriminator, dependency_cls in DEPENDENCY_DISCRIMINATORS.items():
        if discriminator in data:
            return dependency_cls(data)

    raise ValueError(f'unknown dependency definition {data}')


def from_lock(identifier: Identifier, lock: DependencyLock) -> Dependency:
    return build({
        identifier.type: identifier.id,
        'options': lock.current_options
    })


__all__ = ['Dependency', 'Identifier', 'build', 'dependency', 'from_lock']
