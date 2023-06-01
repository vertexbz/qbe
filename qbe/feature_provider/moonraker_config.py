from __future__ import annotations
import qbe.cli as cli
from qbe.handler.service_reload import ServiceReload
from qbe.utils.obj import qrepr
from .mixin.operation import AVAILABLE_STRATEGIES, OperationMixin, OperationConfigMixin
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section


class MoonrakerConfigProviderConfig(OperationConfigMixin):
    def __init__(self, **kw) -> None:
        self.link = self._pop_from_dict(kw, 'link')
        self.blueprint = self._pop_from_dict(kw, 'blueprint')
        self.template = self._pop_from_dict(kw, 'template')

    __repr__ = qrepr()


@feature_provider('moonraker-config')
class MoonrakerConfigProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: dict) -> MoonrakerConfigProviderConfig:
        return MoonrakerConfigProviderConfig(**config)

    def process(self, config: MoonrakerConfigProviderConfig, line: cli.Line, section: Section) -> None:
        for strategy_name, strategy_cls in AVAILABLE_STRATEGIES.items():
            target = self.config.paths.moonraker.configs
            if strategy_name == 'link':
                target = self.config.paths.moonraker.config_links

            if strategy_name in config:
                strategy = strategy_cls(self)
                ops = config[strategy_name]
                if self.process_operation(strategy, ops, target, line, section,
                                          default=self.config.paths.moonraker.config):
                    section.notify(ServiceReload('moonraker.service', restart=True))
