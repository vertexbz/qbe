from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import DataSource
from .git import GitDataSource
from .internal import InternalDataSource
from .local import LocalDataSource
from ...manifest.data_source.git import GitDataSource as ManifestGitDataSource
from ...manifest.data_source.internal import InternalDataSource as ManifestInternalDataSource
from ...manifest.data_source.local import LocalDataSource as ManifestLocalDataSource
from ...manifest.data_source.zip import ZipDataSource as ManifestZipDataSource

if TYPE_CHECKING:
    from ...manifest import ManifestDataSource


def for_local_path_and_manifest(
        path: str,
        data_source: ManifestDataSource,
        package_path: Optional[str] = None
) -> DataSource:
    def inner():
        if isinstance(data_source, ManifestZipDataSource):
            return LocalDataSource(path, url=data_source.url)

        if isinstance(data_source, ManifestGitDataSource):
            return GitDataSource(path, repo=data_source.url, branch=data_source.branch)

        if isinstance(data_source, ManifestInternalDataSource):
            return LocalDataSource(path)

        if isinstance(data_source, ManifestLocalDataSource):
            return LocalDataSource(path)

        raise ValueError(f'Unsupported data source: {type(data_source)}')

    if package_path is not None:
        return InternalDataSource(package_path, inner())

    return inner()


__all__ = ['DataSource', 'for_local_path_and_manifest']
