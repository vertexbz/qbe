from __future__ import annotations
import pkgutil
from typing import Type, TYPE_CHECKING
from .base import BaseUpdater

if TYPE_CHECKING:
    from qbe.config.mcu import AnyMCU
    from qbe.config import Config

AVAILABLE_UPDATERS: dict[str, Type[BaseUpdater]] = {}


def firmware_updater(name):
    def register_function_fn(cls):
        if name in AVAILABLE_UPDATERS:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, BaseUpdater):
            raise ValueError(f'Class {cls} is not a subclass of {BaseUpdater}')
        AVAILABLE_UPDATERS[name] = cls
        return cls

    return register_function_fn


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


def flash(config: Config, mcu: AnyMCU, mode: str, firmware_path: str) -> None:
    if mode not in AVAILABLE_UPDATERS:
        raise ValueError("unknown updater")

    updater = AVAILABLE_UPDATERS[mode]

    updater(config).flash(mcu, firmware_path)
