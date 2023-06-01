from __future__ import annotations
import os
import urllib.request
import zipfile
import tempfile
from .base import BaseProvider, UpdateResult, Dependency
from . import package_provider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qbe.config import ConfigPaths


class ZipDependency(Dependency):
    def __init__(self, paths: ConfigPaths, **kw) -> None:
        super().__init__(paths, kw.pop('local', None), **kw)
        self.zip = kw.pop('zip')


@package_provider('zip')
class Zip(BaseProvider):
    DEPENDENCY = ZipDependency

    def _extract_zip_file(self):
        file_path_or_url = self.config.zip
        if file_path_or_url.startswith('http'):
            # Download the zip file from the URL to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                urllib.request.urlretrieve(file_path_or_url, tmp_file.name)
                zip_file_name = tmp_file.name
        else:
            # Use the local file path
            zip_file_name = file_path_or_url

            # Extract the contents of the zip file to the output directory
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            os.makedirs(self.config.local, exist_ok=True)
            zip_ref.extractall(self.config.local)

            # Delete the temporary file if it was downloaded from a URL
        if file_path_or_url.startswith('http'):
            os.remove(zip_file_name)

    def update(self) -> UpdateResult:
        if os.path.isdir(self.config.local):
            return UpdateResult.NONE

        self._extract_zip_file()
        return UpdateResult.INSTALLED
