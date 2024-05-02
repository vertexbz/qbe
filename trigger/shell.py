from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from . import trigger
from .base import Trigger
from ..adapter.command import shell, sudo, CommandError
from ..adapter.dataclass import field
from ..adapter.yaml import PkgTag
from ..updatable.data_source.internal import InternalDataSource

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress import ProgressRoot


@trigger('shell')
@dataclass(frozen=True)
class ShellTrigger(Trigger):
    command: str = field(name='shell')
    quiet: bool = field(default=False, omitempty=True)
    sudo: bool = field(default=False, omitempty=True)

    @classmethod
    def decode(cls, data: dict):
        return cls(command=data.get('shell'), quiet=data.get('quiet', False), sudo=data.get('sudo', False))

    async def handle(self, progress: ProgressRoot, updatable: Updatable):
        runner = sudo if self.sudo else shell
        source = updatable.source

        workdir = source.path
        if isinstance(self.command, PkgTag) and isinstance(source, InternalDataSource):
            workdir = source.package_path

        env = self._obj_to_env(updatable.template_context())

        try:
            await runner(
                f'sh {self.command}', cwd=workdir, env=env,
                stdout_callback=None if self.quiet else progress.log
            )
        except CommandError as e:
            progress.log_error(f'Command {self.command} failed: {e}')

    @staticmethod
    def _is_valid_attribute(obj, attr: str):
        return not attr.startswith('_') and isinstance(getattr(type(obj), attr), property)

    def _obj_to_env(self, obj: Union[object, dict], prefix: str = 'QBE_') -> dict[str, str]:
        env = {}

        if not isinstance(obj, dict):
            obj = {attr: getattr(obj, attr) for attr in dir(type(obj)) if self._is_valid_attribute(obj, attr)}

        for k, v in obj.items():
            if v is None:
                continue

            if isinstance(v, dict):
                env.update(self._obj_to_env(v, prefix + k.upper() + '_'))
            elif not isinstance(v, (str, int, float, bool)):
                env.update(self._obj_to_env(v, prefix + k.upper() + '_'))
            else:
                env[prefix + k.upper()] = str(v)

        return env
