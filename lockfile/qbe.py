from __future__ import annotations

from dataclasses import dataclass

from .versioned import Versioned


@dataclass
class QBELock(Versioned):
    pass
