import pkgutil
from typing import Type
from .base import BaseProvider

AVAILABLE_PROVIDERS: dict[str, Type[BaseProvider]] = {}


def feature_provider(name):
    def register_function_fn(cls):
        if name in AVAILABLE_PROVIDERS:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, BaseProvider):
            raise ValueError(f'Class {cls} is not a subclass of {BaseProvider}')
        AVAILABLE_PROVIDERS[name] = cls
        return cls

    return register_function_fn


from .system_packages import *
from .system_config import *
from .ansible import *
from .pip_app import *

__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)
