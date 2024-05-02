from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from . import dependency
from .base import Dependency
from ...manifest.data_source.git import GitDataSource

if TYPE_CHECKING:
    from ...manifest import ManifestDataSource


@dependency
class GitDependency(Dependency):
    DISCRIMINATOR = 'git'

    def __init__(self, data: dict):
        super().__init__(data)
        self._branch = data.pop('branch', 'master')

    @property
    def branch(self) -> str:
        return self._branch

    @cached_property
    def data_source(self) -> ManifestDataSource:
        return GitDataSource(url=self.identifier.id, branch=self.branch)
