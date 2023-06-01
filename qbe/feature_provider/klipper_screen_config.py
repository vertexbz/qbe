from __future__ import annotations
from typing import TYPE_CHECKING
import qbe.cli as cli
from qbe.utils.obj import qrepr
from qbe.handler.service_reload import ServiceReload
from .mixin.operation import AVAILABLE_STRATEGIES, OperationMixin, OperationConfigMixin
from . import feature_provider

if TYPE_CHECKING:
    from qbe.package import Section


class KlipperScreenConfigProviderConfig(OperationConfigMixin):
    def __init__(self, **kw) -> None:
        self.link = self._pop_from_dict(kw, 'link')
        self.blueprint = self._pop_from_dict(kw, 'blueprint')
        self.template = self._pop_from_dict(kw, 'template')

    __repr__ = qrepr()


@feature_provider('klipper-screen-config')
class KlipperScreenConfigProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: dict) -> KlipperScreenConfigProviderConfig:
        return KlipperScreenConfigProviderConfig(**config)

    def process(self, config: KlipperScreenConfigProviderConfig, line: cli.Line, section: Section) -> None:
        for strategy_name, strategy_cls in AVAILABLE_STRATEGIES.items():
            target = self.config.paths.klipper_screen.configs
            if strategy_name == 'link':
                target = self.config.paths.klipper_screen.config_links

            if strategy_name in config:
                strategy = strategy_cls(self)
                ops = config[strategy_name]
                if self.process_operation(strategy, ops, target, line, section,
                                          default=self.config.paths.klipper_screen.config):
                    section.notify(ServiceReload('KlipperScreen.service', restart=True))
