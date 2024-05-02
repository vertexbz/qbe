from __future__ import annotations

from abc import abstractmethod
from dataclasses import fields
from functools import cached_property
import hashlib
import logging
import os
import shutil
from typing import TYPE_CHECKING, Optional

from ..adapter.dataclass import encode
from ..adapter.file import readfile
from ..adapter.yaml import load, dump
from ..manifest import Manifest
from ..paths import paths
from ..provider import providers as all_providers
from ..qbefile.utils import find_in
from ..updatable import Updatable
from ..updatable.data_source import for_local_path_and_manifest, DataSource
from ..updatable.data_source.internal import InternalDataSource

if TYPE_CHECKING:
    from updatable.progress import UpdatableProgress
    from ..qbefile.dependency import Dependency
    from ..updatable.identifier import Identifier
    from ..lockfile.dependency import DependencyLock


class Package(Updatable):
    DISCRIMINATOR: Optional[str] = None

    def __init__(self, dependency: Dependency, lock: DependencyLock):
        super().__init__(lock)
        self._dependency = dependency

    @property
    @abstractmethod
    def package_path(self) -> str:
        raise NotImplemented("Not implemented")

    @property
    def lock(self) -> DependencyLock:
        return super().lock  # type: ignore

    @cached_property
    def source(self) -> DataSource:
        if self.manifest.data_source:
            return for_local_path_and_manifest(
                paths.package(self),
                self.manifest.data_source,
                package_path=self.package_path
            )

        return for_local_path_and_manifest(paths.package(self), self._dependency.data_source)

    @cached_property
    def manifest(self):
        return Manifest.decode(load(readfile(find_in(self.package_path))))

    @property
    def identifier(self) -> Identifier:
        return self._dependency.identifier

    @property
    @abstractmethod
    def slug(self):
        raise NotImplemented("Not implemented")

    @property
    def type(self) -> str:
        return self.manifest.type.value

    @property
    def options(self) -> dict:
        return self._dependency.options

    @property
    def options_dirty(self) -> bool:
        return self._dependency.options != self.lock.current_options

    @property
    def recipie_dirty(self) -> bool:
        return self.lock.recipie_hash_installed != self.lock.recipie_hash_current

    async def refresh(self, **kw):
        await super().refresh(**kw)
        self.__dict__.pop('source', None)
        self.__dict__.pop('manifest', None)
        self.__dict__.pop('providers', None)
        self.lock.recipie_hash_current = await self._hash_recipe()

    @cached_property
    def providers(self):
        providers = []

        provider_classes = set(all_providers().values())
        for i, block in enumerate(self.manifest.provides):
            for field in fields(block):
                if (cfg := getattr(block, field.name, None)) and (provider_cls := field.metadata.get('provider', None)):
                    if provider_cls not in provider_classes:
                        raise NotImplementedError('Multiple providers of the same type not supported for now')
                    providers.append(provider_cls(self, cfg))
                    provider_classes.remove(provider_cls)

        for provider_cls in provider_classes:
            providers.append(provider_cls(self, None))

        return providers

    async def update(self, progress: UpdatableProgress, **kw) -> None:
        await super().update(progress, **kw)  # pull

        for provider in self.providers:
            with progress.provider(provider) as p:
                await provider.apply(p)

        if self.manifest.triggers:
            for trigger in self.manifest.triggers.collect(
                options=self.options,
                installed=progress.installed,
                updated=progress.updated
            ):
                progress.notify(trigger.trigger)

        recipe_hash = await self._hash_recipe()
        self.lock.recipie_hash_current = recipe_hash
        self.lock.recipie_hash_installed = recipe_hash
        self.lock.current_options = self.options
        self.lock.current_version = self.lock.remote_version
        self.lock.commits_behind = []

    async def remove(self, progress: UpdatableProgress) -> None:
        progress.mark_removing()

        for provider in reversed(self.providers):
            if not self.lock.provided.has(provider):
                continue

            with progress.provider(provider) as p:
                await provider.remove(p)

        if self.manifest.triggers:
            for trigger in self.manifest.triggers.collect(
                options=self.options,
                removed=progress.removed
            ):
                progress.notify(trigger.trigger)

        with progress.sources(self.source) as p:
            if os.path.exists(self.source.path):
                shutil.rmtree(self.source.path, ignore_errors=True)
                p.log_removed('removed')
            else:
                p.log_unchanged('up to date')

    def template_context(self):
        sup = super().template_context()
        return {
            **sup,
            'dirs': {
                **sup['dirs'],
                'venv': paths.venv(os.path.basename(sup['dirs']['pkg']))
            },
        }

    async def _hash_recipe(self):
        hash_object = hashlib.sha256()
        hash_object.update(dump(encode(self.manifest.data_source), None).strip().encode('utf-8'))
        logging.warning(f'{self.name}, ds: {hash_object.hexdigest()}')
        hash_object.update(dump(encode(self.manifest.provides), None).strip().encode('utf-8'))
        logging.warning(f'{self.name}, provides: {hash_object.hexdigest()}')
        hash_object.update(dump(encode(self.manifest.triggers), None, ).strip().encode('utf-8'))
        logging.warning(f'{self.name}, triggers: {hash_object.hexdigest()}')

        if not isinstance(self.source, InternalDataSource) and not os.path.exists(self.source.path):
            hash_object.update('[UNKNOWN]'.strip().encode('utf-8'))
            return hash_object.hexdigest()

        for provider in self.providers:
            for path in provider.files:
                if isinstance(self.source, InternalDataSource) and not os.path.exists(path):
                    continue

                hash_object.update(readfile(path).encode('utf-8'))

        return hash_object.hexdigest()


__all__ = ['Package']
