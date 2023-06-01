from __future__ import annotations
import os
import git
import git.cmd
from qbe.cli import Error
from giturlparse import parse as giturlparse
from ..base import BaseProvider, UpdateResult, Dependency
from .. import package_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class GitDependency(Dependency):
    def __init__(self, paths: ConfigPaths, **kw) -> None:
        self.remote = kw.pop('git', None)
        self.branch = kw.pop('branch', 'master')
        local = kw.pop('local', None)
        if local is None:
            parsed = giturlparse(self.remote, check_domain=False)
            self._name = os.path.basename(parsed.repo)
            local = 'git-' + parsed.host.replace('.', '-') + '-' + parsed.owner.split('/')[0] + '-' + self._name
        else:
            self._name = os.path.basename(local)

        super().__init__(paths, local, **kw)

    @property
    def name(self):
        return self._name


@package_provider('git')
class Git(BaseProvider):
    DEPENDENCY = GitDependency

    def __init__(self, config: GitDependency) -> None:
        super().__init__(config)
        self._initialized = False
        if os.path.isdir(os.path.join(config.local, '.git')):
            self.repo = git.Repo(config.local)
            if self.repo.remotes.origin.url != config.remote:
                raise Error(f'Local origin url {self.repo.remotes.origin.url} does not match provided {config.remote}')
        else:
            self.repo = git.Repo.init(config.local)
            self.repo.create_remote('origin', config.remote)

    def fetch(self):
        for fetch_info in self.repo.remotes.origin.fetch():
            return fetch_info

    def pull(self):
        for pull_info in self.repo.remotes.origin.pull():
            return pull_info

    def update(self) -> UpdateResult:
        fresh = self.config.branch not in self.repo.branches

        self.fetch()

        if fresh:
            ref = self.repo.remotes.origin.refs[self.config.branch]
            # Setup a local tracking branch of a remote branch
            self.repo.create_head(self.config.branch, ref)
            self.repo.heads[self.config.branch].set_tracking_branch(ref)

        self.repo.heads[self.config.branch].checkout()

        if fresh:
            return UpdateResult.INSTALLED

        local = self.repo.heads[self.config.branch]
        ref = self.repo.remotes.origin.refs[self.config.branch]

        if ref.commit != local.commit:
            self.pull()
            return UpdateResult.UPDATED

        return UpdateResult.NONE
