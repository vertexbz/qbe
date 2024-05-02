from __future__ import annotations

import enum


class PackageType(enum.Enum):
    SERVICE = 'service'
    CONFIG = 'config'
    EXTENSION = 'extension'
    PACKAGE = 'package'
