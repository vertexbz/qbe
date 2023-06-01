from __future__ import annotations

import shlex
from qbe.utils.yaml import PkgTag
from qbe.utils.obj import obj_to_env
from qbe.support import Shell

from .base import BaseTriggerHandler, Trigger
from . import trigger_handler


@trigger_handler('shell')
class ShellHandler(BaseTriggerHandler):
    def _env(self):
        return obj_to_env(self.context)

    def __shell(self, cmd: str):
        if isinstance(cmd, PkgTag):
            return Shell(cwd=self.dependency.qbe_definition, env=self._env())
        else:
            return Shell(cwd=self.dependency.local, env=self._env())

    def _shell(self, cmd: str, quiet: bool):
        shell = self.__shell(cmd)
        if quiet:
            return shell.quiet
        else:
            return shell.run

    def process(self, trigger: Trigger) -> None:
        cmd = trigger['shell']
        script = shlex.split(str(cmd))
        shell = self._shell(cmd, trigger.is_quiet)
        result = shell(script)

        if result.returncode == 0:
            self.section.installed(f'shell: {script[0]}')
        else:
            self.section.error(str(result.stderr).strip())
