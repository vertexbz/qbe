from __future__ import annotations
import time
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.task_result import TaskResult
from ansible.playbook import Playbook
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible.errors import AnsibleError
from ansible import context
import qbe.cli as cli
from qbe.utils.obj import qrepr
from qbe.utils.yaml import PkgTag
from .base import BaseProvider
from . import feature_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.package import Section

context.CLIARGS = ImmutableDict(
    connection='local',
    syntax=False,
    forks=10,
    become=None,
    start_at_task='*',
    become_method='sudo',
    become_user='root',
    check=False,
    diff=False,
    verbosity=0
)


class AnsibleProviderConfig:
    def __init__(self, playbook: str) -> None:
        super().__init__()
        self.playbook = playbook

    __repr__ = qrepr()


class ResultsCollectorCallback(CallbackBase):
    def __init__(self, section: Section):
        super().__init__()
        self.section = section
        self.tasks: list[TaskResult] = []

    def v2_runner_on_ok(self, task: TaskResult, *args, **kwargs):
        if task.is_changed():
            self.section.updated(task.task_name + ': updated')
        else:
            self.section.unchanged(task.task_name + ': up to date')

    def v2_runner_on_failed(self, task: TaskResult, *args, **kwargs):
        self.section.error(task.task_name + ': ' + task._result.get('msg', 'ERROR'))


@feature_provider('ansible')
class AnsibleProvider(BaseProvider):
    @classmethod
    def validate_config(cls, config: str) -> AnsibleProviderConfig:
        if not isinstance(config, (str, PkgTag)):
            raise ValueError('Invalid configuration for ansible provider')
        return AnsibleProviderConfig(config)

    def process(self, config: AnsibleProviderConfig, line: cli.Line, section: Section) -> None:
        line.print(cli.dim('executing playbook...'))
        time.sleep(0.25)

        loader = DataLoader()
        results_callback = ResultsCollectorCallback(section)
        inventory = InventoryManager(loader=loader, sources='localhost,')
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        variable_manager.extra_vars.update({'qbe': self._context()})

        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords={},
            stdout_callback=results_callback
        )

        pb = Playbook.load(self._src_path(config.playbook), variable_manager=variable_manager, loader=loader)

        try:
            for play in pb.get_plays():
                tqm.run(play)
        except AnsibleError as e:
            section.error(e.message)
        finally:
            tqm.cleanup()
            if loader:
                loader.cleanup_all_tmp_files()
