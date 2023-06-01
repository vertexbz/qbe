from __future__ import annotations
import os
import time
from typing import TYPE_CHECKING
import qbe.cli as cli
from qbe.support import sudo_write
from qbe.utils import jinja
from qbe.handler.service_reload import ServiceReload
from ..base import ConfigOperation, BaseProvider

if TYPE_CHECKING:
    from qbe.package import Section


class ServicesConfigMixin:
    def __init__(self, **kw) -> None:
        super().__init__()
        self.services: list[ConfigOperation] = [ConfigOperation(link) for link in kw.pop('services', [])]


class ServicesMixin(BaseProvider):
    def process_services(self, config: ServicesConfigMixin, line: cli.Line, section: Section):
        if len(config.services) > 0:
            line.print(cli.dim('installing systemd services...'))
            time.sleep(0.25)

            for service in config.services:
                source = self._src_path(service.source)
                content = open(source, 'r', encoding='utf-8').read()
                content = jinja.render(content, self._context())
                target = os.path.join('/etc/systemd/system', service.target)

                if not os.path.exists(target):
                    sudo_write(content, target)
                    section.installed(f'service: {service.target} installed')
                    section.notify(ServiceReload(os.path.join(service.target)))
                elif open(target, 'r', encoding='utf-8').read() != content:
                    sudo_write(content, target)
                    section.updated(f'service: {service.target} updated')
                    section.notify(ServiceReload(os.path.join(service.target), restart=True, daemon_reload=True))
                else:
                    section.unchanged(f'service: {service.target} up to date')
