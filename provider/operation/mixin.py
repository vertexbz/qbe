from __future__ import annotations

from abc import ABC
from asyncio import iscoroutine
from dataclasses import fields, dataclass
import os
from typing import TYPE_CHECKING, Optional, TypeVar, Union

from .. import Provider
from ..base import Config
from ...adapter.command import shell
from ...adapter.yaml import VarTag
from ...updatable.progress.formatter import MessageType

if TYPE_CHECKING:
    from .operation import SrcDst
    from ...updatable.progress.provider.interface import IProviderProgress
    from ...lockfile.provided.provider_provided import Entry


@dataclass
class TargetPath:
    main: str
    link: Optional[str] = None


T = TypeVar('T', bound=Config)


class OperationMixin(Provider[T], ABC):
    async def apply_operations(self, progress: IProviderProgress, target: str, link_target: Optional[str] = None):
        changed = False
        for field in self._current_config_fields():
            operations: list[SrcDst] = getattr(self._config, field.name, [])

            if len(operations) > 0 and (handler := field.metadata.get('operation_handler', None)):
                with progress.sub(field.name) as p:
                    for operation in operations:
                        if not operation.available(self._updatable.options):
                            continue

                        op_target = self._target_path(operation.target)
                        with p.sub(op_target, case=True) as pp:
                            source = self._src_path(operation.source)

                            if field.metadata.get('link_target', False) and link_target:
                                target = link_target

                            if isinstance(operation.target, VarTag):
                                destination = op_target
                            else:
                                destination = os.path.join(target, op_target)

                            exists = os.path.exists(destination)
                            result = handler(source, destination, self._updatable.template_context())
                            if iscoroutine(result):
                                result = await result
                            if result:
                                pp.log_changed('updated' if exists else 'created', input=source, output=destination)
                                changed = True
                            else:
                                pp.log_unchanged('already exists', input=source, output=destination)

        return await self._cleanup_operations(progress, progress.untouched) or changed

    async def remove_operations(self, progress: IProviderProgress) -> bool:
        return await self._cleanup_operations(progress, progress.provided)

    async def _cleanup_operations(self, progress: IProviderProgress, items: set[Entry]) -> bool:
        changed = False
        for field in self._config_fields():
            removable = field.metadata.get('removable', False)

            field_items = list(filter(lambda item: item.path[0] == field.name, items))
            if not field_items:
                continue

            with progress.sub(field.name) as p:
                for entry in field_items:
                    with p.sub(entry.output, case=True) as pp:
                        if removable:
                            await self._remove_entry(entry)
                            pp.log_removed('removed', entry)
                        else:
                            pp.log_removed('retained', entry, typ=MessageType.WARNING)
                        changed = True

        return changed

    async def _remove_entry(self, entry: Entry):
        path = entry.output
        if not path.startswith('/'):
            raise RuntimeError('path must be absolute')
        await shell('rm -rf ' + path)

    @property
    def files(self) -> list[str]:
        result = []

        for field in self._current_config_fields():
            if not field.metadata.get('tracked', False):
                continue

            operations: list[SrcDst] = getattr(self._config, field.name, [])
            for operation in operations:
                result.append(self._src_path(operation.source))

        return result

    def _current_config_fields(self):
        return fields(self._config) if self._config else []

    def _config_fields(self):
        return fields(self._config) if self._config else fields(self.CONFIG)

    def _target_path(self, op_target: Union[str, VarTag]):
        if isinstance(op_target, VarTag):
            tmp = op_target.in_dict(self._updatable.template_context())
            if not isinstance(tmp, str):
                raise ValueError('invalid variable ' + op_target.variable)
            return tmp

        return op_target
