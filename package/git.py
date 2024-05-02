from __future__ import annotations

from functools import cached_property
import io
import re
import subprocess
import tarfile
from typing import TYPE_CHECKING
import urllib.parse

from . import package
from .base import Package
from ..adapter.yaml import load
from ..manifest import Manifest
from ..paths import paths
from ..qbefile.utils import CONFIG_FILE_NAMES

if TYPE_CHECKING:
    from ..qbefile.dependency.git import GitDependency


pattern_host = re.compile(r"(?:@|//)([^:/]+)[:/]([^:/]+)", re.MULTILINE)
pattern_name = re.compile(r"([^:/]+?)(?:\.git)?$", re.MULTILINE)


@package
class GitPackage(Package):
    DISCRIMINATOR = 'git'
    _dependency: GitDependency

    @property
    def package_path(self) -> str:
        return paths.package(self)

    @cached_property
    def manifest(self):
        try:
            return super().manifest
        except:
            return Manifest.decode(self._load_remote_manifest())

    @property
    def slug(self):
        match = next(pattern_host.finditer(self._dependency.identifier.id))
        host = match.group(1)
        owner = match.group(2)
        name = next(pattern_name.finditer(self._dependency.identifier.id)).group(1)

        return 'git-' + host.replace('.', '-') + '-' + owner.replace('.', '-') + '-' + name.replace('.', '-')

    @property
    def name(self) -> str:
        url = urllib.parse.urlparse(self._dependency.identifier.id)
        path = url.path[1:]

        if path.endswith('.git'):
            path = path[:-4]

        return self.manifest.name or path.split('/')[-1]

    def _load_remote_manifest(self):
        for file_name in CONFIG_FILE_NAMES:
            command = f"git archive --remote={self._dependency.identifier.id} {self._dependency.branch} {file_name}"
            try:
                tarball = subprocess.check_output(command, shell=True)
                tar = tarfile.open(fileobj=io.BytesIO(tarball))
                file = tar.extractfile(file_name)
                return load(file.read().decode())
            except subprocess.CalledProcessError:
                pass
        else:
            raise ValueError("None of the files exist in the repository.")
