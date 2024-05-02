from __future__ import annotations

import enum


class PackageStatus(enum.Enum):
    UNKNOWN = 'unknown'
    STARTED = 'started'
    UPDATING = 'updating'
    INSTALLING = 'installing'
    REMOVING = 'removing'
    FINISHED = 'finished'

    def unfinished(self) -> bool:
        return self in (PackageStatus.STARTED, PackageStatus.UPDATING, PackageStatus.INSTALLING)
