from __future__ import annotations
import os
import time
import pkgutil
from typing import Type, TYPE_CHECKING, Union
from .base import BaseStrategy, Skipped, StrategyException
import qbe.cli as cli
from ...base import ConfigOperation, BaseProvider

if TYPE_CHECKING:
    from qbe.package import Section

AVAILABLE_STRATEGIES: dict[str, Type[BaseStrategy]] = {}


def operation(name: str):
    def register_function_fn(cls):
        if name in AVAILABLE_STRATEGIES:
            raise ValueError(f'Name {name} already registered!')
        if not issubclass(cls, BaseStrategy):
            raise ValueError(f'Class {cls} is not a subclass of {BaseStrategy}')

        setattr(cls, 'name', name)

        AVAILABLE_STRATEGIES[name] = cls
        return cls

    return register_function_fn


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    if not module.endswith('.base'):
        __import__(module)


class OperationConfigMixin:
    def _load_list(self, config: list[Union[str, list[str, str]]]) -> list[ConfigOperation]:
        return [ConfigOperation(link) for link in config]

    def _pop_from_dict(self, config: dict, key: str) -> list[ConfigOperation]:
        return self._load_list(config.pop(key, []))

    def __contains__(self, item: str):
        if hasattr(self, item):
            attr = getattr(self, item)
            if isinstance(attr, list):
                return len(attr) > 0
            return True

        return False

    def __getitem__(self, key: str) -> list[ConfigOperation]:
        return getattr(self, key)


class OperationMixin(BaseProvider):
    def process_operation(
        self,
        strategy: BaseStrategy,
        operations: list[ConfigOperation],
        target: str,
        line: cli.Line,
        section: Section,
        default: str = None
    ) -> bool:
        changed = False
        if len(operations) > 0:
            line.print(cli.dim(f'processing {strategy.name}...'))
            time.sleep(0.25)

            for operation in operations:
                if not operation.available(self.dependency.options):
                    continue

                if operation.target is True and default is None:
                    raise StrategyException('No default config available')

                if operation.target is True:
                    readable_target = os.path.join(os.path.basename(os.path.dirname(default)),
                                                   os.path.basename(default))
                else:
                    readable_target = os.path.join(os.path.basename(target), str(operation.target))

                interpolations = {
                    'source': cli.bold(
                        os.path.join(os.path.basename(self._base_path(operation.source)), str(operation.source))),
                    'target': cli.bold(readable_target),
                }

                source = self._src_path(operation.source)
                if operation.target is True:
                    destination = default
                else:
                    destination = os.path.join(target, str(operation.target))

                try:
                    result = strategy.execute(source, destination)
                    changed = True
                    section.updated(f'{cli.dim(strategy.name + ":")} {result % interpolations}')
                except Skipped as exc:
                    dim_interpolations = {key: interpolations[key] + cli.CODE_DIM for key in interpolations}
                    section.unchanged(f'{strategy.name}: {exc.reason % dim_interpolations}')
                except Exception as exc:
                    line.pre_error()
                    line.finish()
                    raise exc

        return changed
