from __future__ import annotations
import pkgutil
from typing import TYPE_CHECKING
from .base import AnyTriggerHandler, BaseTriggerHandler, Trigger

if TYPE_CHECKING:
    from qbe.package_provider import Dependency
    from qbe.config import Config
    from qbe.package import Section, Package

AVAILABLE_TRIGGERS: dict[str, AnyTriggerHandler.__class__] = {}


def trigger_handler(name):
    def register_function_fn(cls):
        if name in AVAILABLE_TRIGGERS:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, BaseTriggerHandler):
            raise ValueError(f'Class {cls} is not a subclass of {BaseTriggerHandler}')
        AVAILABLE_TRIGGERS[name] = cls
        return cls

    return register_function_fn


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


def build_trigger(config: dict):
    return Trigger(config)


def build_triggers(config: list[dict]):
    return [build_trigger(trg) for trg in config]


def multihandler(
    config: Config,
    package: Package,
    dependency: Dependency,
    section: Section,
    messages: list[str]
):
    handlers: dict[str, AnyTriggerHandler] = {}

    def handler(trigger: Trigger):
        for discriminator in AVAILABLE_TRIGGERS:
            if discriminator not in trigger:
                continue

            if discriminator not in handlers:
                handler_cls = AVAILABLE_TRIGGERS[discriminator]
                handlers[discriminator] = handler_cls(config, package, dependency, section, messages)

            return handlers[discriminator].process(trigger)

    return handler
