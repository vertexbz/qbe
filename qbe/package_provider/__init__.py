from __future__ import annotations
import pkgutil
from typing import Type, Union
from .base import BaseProvider, Dependency, UpdateResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.config import ConfigPaths

AVAILABLE_PROVIDERS: dict[str, Type[BaseProvider]] = {}


def package_provider(name):
    def register_function_fn(cls):
        if name in AVAILABLE_PROVIDERS:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, BaseProvider):
            raise ValueError(f'Class {cls} is not a subclass of {BaseProvider}')
        if not cls.DEPENDENCY:
            raise ValueError('Provider must provide dependency class')
        AVAILABLE_PROVIDERS[name] = cls
        return cls

    return register_function_fn


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base') and not module.endswith('.local'):
        __import__(module)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if module.endswith('.local'):
        __import__(module)


def build_dependency(config: dict, paths: ConfigPaths) -> Type[Dependency]:
    for discriminator, provider_cls in AVAILABLE_PROVIDERS.items():
        if discriminator in config:
            return provider_cls.DEPENDENCY(paths, **config)

    raise ValueError(f'unknown dependency definition {config}')


def dependency_provider(dep: Dependency) -> Union[BaseProvider, None]:
    if dep.__class__ is Dependency:
        return None

    for provider_cls in AVAILABLE_PROVIDERS.values():
        if dep.__class__ is provider_cls.DEPENDENCY:
            return provider_cls

    return None
