from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .provided import Provided
from ..adapter.dataclass import UniversalDecoder, field
from ..updatable.data_source.git import TaggedCommit
from ..updatable.progress.package_status import PackageStatus


@dataclass
class Versioned(UniversalDecoder):
    refresh_time: float = 0.0
    current_version: str = '?'
    remote_version: str = '?'
    commits_behind: list[TaggedCommit] = field(default_factory=list, decoder=lambda v: [TaggedCommit(**c) for c in v])
    last_error: Optional[str] = None
    status: PackageStatus = field(default=PackageStatus.UNKNOWN)
    provided: Provided = field(default_factory=Provided)

    def update(self, data: dict) -> None:
        data = self._decode_params(data)
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
