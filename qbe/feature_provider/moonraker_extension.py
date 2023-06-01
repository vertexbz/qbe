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


class MoonrakerExtensionProviderConfig(OperationConfigMixin):
    def __init__(self, links: list) -> None:
        self.links = self._load_list(links)

    __repr__ = qrepr()


@feature_provider('moonraker-extension')
class MoonrakerExtensionProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: list) -> MoonrakerExtensionProviderConfig:
        if not isinstance(config, list):
            raise ValueError('Invalid configuration for moonraker-extension provider')
        return MoonrakerExtensionProviderConfig(config)

    def process(self, config: MoonrakerExtensionProviderConfig, line: cli.Line, section: Section) -> None:
        target = self.config.paths.moonraker.extensions
        if self.process_operation(LinkStrategy(self), config.links, target, line, section):
            section.notify(ServiceReload('moonraker.service', restart=True))
