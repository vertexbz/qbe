from __future__ import annotations
import os
import qbe.cli as cli
from qbe.utils.obj import qrepr
from qbe.utils import jinja
from qbe.support import sudo_write, sudo_mkdir, sudo_ln, sudo_rm
from .base import ConfigOperation
from .mixin.operation import BaseStrategy, OperationMixin, OperationConfigMixin, Skipped
from . import feature_provider
from typing import TYPE_CHECKING

from ..utils.file import readfile

if TYPE_CHECKING:
    from qbe.package import Section


class SystemConfigProviderConfig(OperationConfigMixin):
    def __init__(self, **kw) -> None:
        self.link: list[ConfigOperation] = [ConfigOperation(link) for link in kw.pop('link', [])]
        self.blueprint: list[ConfigOperation] = [ConfigOperation(bp) for bp in kw.pop('blueprint', [])]

    def __contains__(self, item: str):
        if item == 'link' and len(self.link) > 0:
            return True
        if item == 'blueprint' and len(self.blueprint) > 0:
            return True

        return False

    def __getitem__(self, key: str) -> list[ConfigOperation]:
        if key == 'link':
            return self.link
        if key == 'blueprint':
            return self.blueprint

        return []

    __repr__ = qrepr()


class BlueprintOperation(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.exists(target):
            raise Skipped('%(target)s already exists')

        contents = readfile(source)
        contents = jinja.render(contents, self.provider._context())
        sudo_mkdir(os.path.dirname(target), recursive=True)
        sudo_write(contents, target)
        return 'created %(target)s from template'

    name = 'blueprint'


class LinkOperation(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.islink(target) and os.readlink(target) == source:
            raise Skipped('%(target)s already links to %(source)s')

        if os.path.exists(target):
            sudo_rm(target, force=True)
        else:
            sudo_mkdir(os.path.dirname(target), recursive=True)

        sudo_ln(source, target, symbolic=True)
        return 'linked %(source)s to %(target)s'

    name = 'link'


@feature_provider('system-config')
class SystemConfigProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: dict) -> SystemConfigProviderConfig:
        return SystemConfigProviderConfig(**config)

    def process(self, config: SystemConfigProviderConfig, line: cli.Line, section: Section) -> None:
        target = '/'

        operations = {
            BlueprintOperation.name: BlueprintOperation(self),
            LinkOperation.name: LinkOperation(self)
        }

        for strategy_name, strategy in operations.items():
            if strategy_name in config:
                self.process_operation(strategy, config[strategy_name], target, line, section)
