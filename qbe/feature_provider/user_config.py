from __future__ import annotations
import os
import qbe.cli as cli
from qbe.utils.obj import qrepr
from qbe.utils import jinja
from qbe.support import sudo_write, sudo_mkdir, sudo_ln, sudo_rm
from .base import ConfigOperation
from .mixin.operation import BaseStrategy, OperationMixin, OperationConfigMixin, AVAILABLE_STRATEGIES
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section


class UserConfigProviderConfig(OperationConfigMixin):
    def __init__(self, **kw) -> None:
        self.link = self._pop_from_dict(kw, 'link')
        self.blueprint = self._pop_from_dict(kw, 'blueprint')
        self.template = self._pop_from_dict(kw, 'template')

    __repr__ = qrepr()


@feature_provider('user-config')
class UserConfigProvider(OperationMixin):
    @classmethod
    def validate_config(cls, config: dict) -> UserConfigProviderConfig:
        return UserConfigProviderConfig(**config)

    def process(self, config: UserConfigProviderConfig, line: cli.Line, section: Section) -> None:
        target = os.path.expanduser('~')

        for strategy_name, strategy_cls in AVAILABLE_STRATEGIES.items():
            if strategy_name in config:
                strategy = strategy_cls(self)
                self.process_operation(strategy, config[strategy_name], target, line, section)
