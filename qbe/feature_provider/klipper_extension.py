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


class KlipperExtensionProviderConfig(OperationConfigMixin):
    def __init__(self, links: list) -> None:
        self.links = self._load_list(links)

    __repr__ = qrepr()


@feature_provider('klipper-extension')
class KlipperExtensionProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: list) -> KlipperExtensionProviderConfig:
        if not isinstance(config, list):
            raise ValueError('Invalid configuration for klipper-extension provider')
        return KlipperExtensionProviderConfig(config)

    def process(self, config: KlipperExtensionProviderConfig, line: cli.Line, section: Section) -> None:
        target = self.config.paths.klipper.extensions
        if self.process_operation(LinkStrategy(self), config.links, target, line, section):
            section.notify(ServiceReload('klipper.service', restart=True))
