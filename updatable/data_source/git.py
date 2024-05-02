from __future__ import annotations

from dataclasses import dataclass
import os.path
import time
from typing import TYPE_CHECKING, Optional

from .base import DataSource
from ...adapter.command import shell

if TYPE_CHECKING:
    from ...lockfile.versioned import Versioned


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    date: str
    subject: str
    message: str


@dataclass(frozen=True)
class TaggedCommit(Commit):
    tag: Optional[str]

    @classmethod
    def from_commit(cls, commit: Commit, tag: Optional[str] = None) -> TaggedCommit:
        return cls(commit.sha, commit.author, commit.date, commit.subject, commit.message, tag)


class GitDataSource(DataSource):
    MAX_COMMITS = 30
    GIT_LOG_FMT = (
        "\"sha:%H%x1Dauthor:%an%x1Ddate:%ct%x1Dsubject:%s%x1Dmessage:%b%x1E\""
    )
    GIT_REF_FMT = (
        "'%(if)%(*objecttype)%(then)%(*objecttype) %(*objectname)"
        "%(else)%(objecttype) %(objectname)%(end) %(refname)'"
    )

    def __init__(self, path: str, repo: Optional[str] = None, branch: Optional[str] = None) -> None:
        super().__init__(path)
        self._branch = branch
        self._url = repo

    @property
    def branch(self) -> str:
        return self._branch

    @property
    def has_change_history(self) -> bool:
        return True

    async def refresh(self, lock: Versioned, stdout_callback=None) -> None:
        if os.path.exists(self.path):
            await shell(f"git fetch --prune --progress origin", cwd=self.path, stdout_callback=stdout_callback)

            if not self._branch:
                self._branch = await self.get_branch()

            lock.current_version = await self.local_version()
            lock.remote_version = await self.remote_version()
            lock.commits_behind = await self.new_commits()
        else:
            if stdout_callback:
                stdout_callback(f'No local copy in "{self.path}"')

            lock.current_version = '?'
            lock.remote_version = await self.remote_remote_version(self._branch or 'master')
            lock.commits_behind = []
        lock.refresh_time = time.time()

    async def update(self, lock: Versioned, stdout_callback=None) -> bool:
        if lock.current_version != '?' and lock.remote_version != '?' and lock.remote_version == lock.current_version:
            return False

        branch = self._branch or 'master'
        if not os.path.exists(self.path):
            if stdout_callback:
                stdout_callback('Cloning repository...')

            os.mkdir(self.path)
            await shell('git init', cwd=self.path)
            await shell(f'git remote add origin {self._url}', cwd=self.path, stdout_callback=stdout_callback)
            await shell('git fetch --progress origin', cwd=self.path, stdout_callback=stdout_callback, stderr_callback=stdout_callback)
            await shell(f'git checkout -b {branch}', cwd=self.path, stdout_callback=stdout_callback)
            await shell(f'git reset --hard origin/{branch}', cwd=self.path, stdout_callback=stdout_callback)

            if stdout_callback:
                stdout_callback('Repository cloned!')
            return True

        try:
            await shell(f'git diff --quiet HEAD..origin/{branch}', cwd=self.path)
            return False
        except:
            if stdout_callback:
                stdout_callback('Updating repository...')

            await shell(f'git reset --hard origin/{branch}', cwd=self.path, stdout_callback=stdout_callback)

            if stdout_callback:
                stdout_callback('Repository updated successfully!')

        return True

    async def get_branch(self):
        return await shell('git rev-parse --abbrev-ref HEAD', cwd=self.path, strip=True)

    async def local_version(self):
        return await shell('git describe --always --tags --long --abbrev=8 --dirty', cwd=self.path, strip=True)

    async def remote_version(self):
        return await shell(f"git describe --always --tags --long --abbrev=8 origin/{self._branch}", cwd=self.path, strip=True)

    async def remote_remote_version(self, branch: str):
        hash_long = (await shell(f"git ls-remote --refs {self._url} {branch}", strip=True)).split(' ', maxsplit=1)[0]
        hash_short = hash_long[:8]

        try:
            version = (await shell(f"git ls-remote --tags --sort=-v:refname {self._url} | head -n 1", strip=True)).split('/')[-1]
            if version:
                return version.replace('^{}', '') + '-g' + hash_short
        except:
            pass

        return hash_short

    async def new_commits(self):
        commits_behind_count = 0

        to_ref = f'origin/{self._branch}'
        current_commit = await self.rev_parse("HEAD")
        upstream_commit = await self.rev_parse(to_ref)

        if upstream_commit != "?":
            rl_args = f"HEAD..{upstream_commit} --count"
            commits_behind_count = int(await self.rev_list(rl_args))

        # Get Commits Behind
        commits_behind: list[TaggedCommit] = []
        if commits_behind_count > 0:
            cbh = await self.get_commits_behind(current_commit, to_ref)
            tagged_commits = await self.get_tagged_commits()
            for i, commit in enumerate(cbh):
                tag = tagged_commits.get(commit.sha, None)
                if i < self.MAX_COMMITS or tag is not None:
                    commits_behind.append(TaggedCommit.from_commit(commit, tag))

        return commits_behind

    async def get_tagged_commits(self, count: int = MAX_COMMITS):
        cnt_arg = f"--count={count} " if count > 0 else ""
        command = f"git for-each-ref {cnt_arg}--sort='-creatordate' --contains=HEAD --merged=origin/{self._branch} --format={self.GIT_REF_FMT} 'refs/tags'"
        resp = await shell(command, cwd=self.path)

        tagged_commits: dict[str, str] = {}
        for line in resp.split('\n'):
            parts = line.strip().split()
            if len(parts) != 3 or parts[0] != "commit":
                continue
            sha, ref = parts[1:]
            tag = ref.split('/')[-1]
            tagged_commits[sha] = tag

        # Return tagged commits as SHA keys mapped to tag values
        return tagged_commits

    async def get_commits_behind(self, current_commit: str, to_ref: str, paths: list[str] = None):
        command = f"git log {current_commit}..{to_ref} --format={self.GIT_LOG_FMT} --max-count={self.MAX_COMMITS}"
        if paths:
            command = f'{command} -- {" ".join(paths)}'

        resp = await shell(command, cwd=self.path)
        commits_behind: list[Commit] = []
        for log_entry in resp.split('\x1E'):
            log_entry = log_entry.strip()
            if not log_entry:
                continue
            log_items = [li.strip() for li in log_entry.split('\x1D')
                         if li.strip()]
            cbh = [li.split(':', 1) for li in log_items]
            commits_behind.append(Commit(**dict(cbh)))
        return commits_behind

    async def rev_parse(self, args: str = ""):
        return await shell(f"git rev-parse {args}".strip(), cwd=self.path, strip=True)

    async def rev_list(self, args: str = ""):
        return await shell(f"git rev-list {args}".strip(), cwd=self.path, strip=True)
