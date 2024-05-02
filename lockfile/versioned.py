from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .provided import Provided
from ..adapter.dataclass import field
from ..updatable.data_source.git import TaggedCommit
from ..updatable.progress.package_status import PackageStatus


@dataclass
class Versioned:
    refresh_time: float = 0.0
    current_version: str = '?'
    remote_version: str = '?'
    commits_behind: list[TaggedCommit] = field(default_factory=list)
    last_error: Optional[str] = None
    status: PackageStatus = field(default=PackageStatus.UNKNOWN)
    provided: Provided = field(default_factory=Provided)

    @classmethod
    def decode(cls, data: dict):
        commits = [TaggedCommit(**c) for c in data.pop('commits_behind', [])]
        status = PackageStatus(data.pop('status', 'unknown'))
        provided = Provided.decode(data.pop('provided', {}))
        return cls(
            **{k.replace('-', '_'): v for k, v in data.items()},
            commits_behind=commits, status=status, provided=provided
        )
