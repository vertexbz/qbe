from __future__ import annotations
from qbe.utils.obj import qrepr
from qbe.handler.service_reload import ServiceReload
import qbe.cli as cli
from .mixin.operation import OperationMixin, OperationConfigMixin
from .mixin.operation.link import LinkStrategy
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section


class KlipperScreenThemeProviderConfig(OperationConfigMixin):
    def __init__(self, links: list) -> None:
        self.links = self._load_list(links)

    __repr__ = qrepr()


@feature_provider('klipper-screen-theme')
class KlipperScreenThemeProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: list) -> KlipperScreenThemeProviderConfig:
        if not isinstance(config, list):
            raise ValueError('Invalid configuration for klipper-screen-theme provider')
        return KlipperScreenThemeProviderConfig(config)

    def process(self, config: KlipperScreenThemeProviderConfig, line: cli.Line, section: Section) -> None:
        target = self.config.paths.klipper_screen.themes
        if self.process_operation(LinkStrategy(self), config.links, target, line, section):
            section.notify(ServiceReload('KlipperScreen.service', restart=True))
