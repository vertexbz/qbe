from __future__ import annotations

import os
import re
import time
from typing import TYPE_CHECKING, Optional

from .git import GitDataSource, TaggedCommit
from ...paths import paths

if TYPE_CHECKING:
    from ...lockfile.versioned import Versioned


class MCUDataSource(GitDataSource):
    async def refresh(self, lock: Versioned, **kw) -> None:
        if lock.current_version == '?':
            return

        if re.match(r'^([a-f0-9]{8})$', lock.current_version):
            commit_ref = lock.current_version
        else:
            commit_ref = re.match(r'.*-g([a-f0-9]{8})$', lock.current_version).group(1)

        self._branch = await self.get_branch()
        lock.commits_behind = await self.commits_since(commit_ref, paths=['src', 'lib', 'Makefile'])

        if len(lock.commits_behind) == 0:
            lock.remote_version = lock.current_version
        else:
            lock.remote_version = await self.local_version()

        lock.refresh_time = time.time()

    async def update(self, lock: Versioned, **kw) -> bool:
        os.makedirs(paths.firmwares, exist_ok=True)
        return False

    async def commits_since(self, since_ref: str, to_ref: str = 'HEAD', paths: Optional[list[str]] = None):
        rl_args = f"{since_ref}..{to_ref} --count"
        commits_behind_count = int(await self.rev_list(rl_args))

        # Get Commits Behind
        commits_behind: list[TaggedCommit] = []
        if commits_behind_count > 0:
            cbh = await self.get_commits_behind(since_ref, to_ref=to_ref, paths=paths)
            tagged_commits = await self.get_tagged_commits()
            for i, commit in enumerate(cbh):
                tag = tagged_commits.get(commit.sha, None)
                if i < self.MAX_COMMITS or tag is not None:
                    commits_behind.append(TaggedCommit.from_commit(commit, tag))

        return commits_behind
