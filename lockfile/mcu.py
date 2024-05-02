from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .versioned import Versioned
from ..adapter.dataclass import field


@dataclass
class MCULock(Versioned):
    current_options: dict[str, Any] = field(default_factory=dict)
