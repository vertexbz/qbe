from __future__ import annotations

from typing import NamedTuple

from .dependency import Dependency
from .mcu import BaseMCU


class Changed(NamedTuple):
    packages: list[Dependency]
    mcus: list[BaseMCU]

    @classmethod
    def new(cls):
        return cls(packages=[], mcus=[])


class Changes(NamedTuple):
    added: Changed
    removed: Changed

    @classmethod
    def new(cls):
        return cls(added=Changed.new(), removed=Changed.new())
