from __future__ import annotations

from typing import TYPE_CHECKING

from .package_status import PackageStatus
from .provider import ProviderProgress
from .source import SourcesProgress

if TYPE_CHECKING:
    from ...provider.base import Provider
    from ...trigger import Trigger
    from ...updatable import Updatable
    from ...updatable.progress import ProgressRoot


class UpdatableProgress:
    def __init__(self, parent: ProgressRoot, updatable: Updatable) -> None:
        self._parent = parent
        self._formatter = parent._formatter
        self._updatable = updatable

    @property
    def installed(self) -> bool:
        return self._updatable.lock.status == PackageStatus.INSTALLING

    @property
    def updated(self) -> bool:
        return self._updatable.lock.status == PackageStatus.UPDATING

    @property
    def removed(self) -> bool:
        return self._updatable.lock.status == PackageStatus.REMOVING

    def __enter__(self) -> UpdatableProgress:
        self._updatable.lock.last_error = None

        if self._updatable.lock.status in (PackageStatus.FINISHED, PackageStatus.UNKNOWN):
            self._updatable.lock.status = PackageStatus.STARTED
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        status = self._updatable.lock.status

        if exc_type is not None:
            self._updatable.lock.last_error = str(exc_value)
        elif self._updatable.lock.status == PackageStatus.REMOVING:
            del self._parent._lockfile.requires[self._updatable.identifier]
        else:
            self._updatable.lock.status = PackageStatus.FINISHED

        self._parent._lockfile.save()

        if status == PackageStatus.INSTALLING:
            self._parent.mark_installed()
        if status == PackageStatus.UPDATING:
            self._parent.mark_updated()
        if status == PackageStatus.REMOVING:
            self._parent.mark_removed()
        # return True # to skip package

    def log(self, message: str, _is_toplevel=True) -> None:
        if _is_toplevel:
            message = self._formatter.format_log(message)

        return self._parent.log(self._formatter.format_updatable(self._updatable) + message)

    def notify(self, trigger: Trigger) -> None:
        return self._parent.notify(trigger, self._updatable)

    def provider(self, provider: Provider) -> ProviderProgress:
        return ProviderProgress(self, provider, self._updatable.lock.provided.by(provider))

    def mark_changed(self) -> None:
        if self._updatable.lock.status == PackageStatus.STARTED:
            self._updatable.lock.status = PackageStatus.UPDATING

    def mark_installing(self) -> None:
        if self._updatable.lock.status in (PackageStatus.STARTED, PackageStatus.UPDATING):
            self._updatable.lock.status = PackageStatus.INSTALLING

    def mark_removing(self):
        if self._updatable.lock.status in (PackageStatus.STARTED, PackageStatus.UPDATING):
            self._updatable.lock.status = PackageStatus.REMOVING

    def sources(self, data_source):
        return SourcesProgress(self, data_source)
