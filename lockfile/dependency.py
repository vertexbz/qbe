from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .versioned import Versioned
from ..adapter.dataclass import field


@dataclass
class DependencyLock(Versioned):
    current_options: dict[str, Any] = field(default_factory=dict)
    recipie_hash_installed: Optional[str] = field(default=None, name='recipie-hash-installed', omitempty=True)
    recipie_hash_current: Optional[str] = field(default=None, name='recipie-hash-current', omitempty=True)

    def is_installed(self):
        return not self.provided.is_empty() or self.current_version != '?'
