from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from typing import TYPE_CHECKING, Optional
import urllib.request
import zipfile

from . import DataSource
from ...adapter.fetch import get
from ...adapter.file import readfile

if TYPE_CHECKING:
    from ...lockfile.versioned import Versioned


class LocalDataSource(DataSource):
    def __init__(self, path: str, url: Optional[str] = None) -> None:
        super().__init__(path)
        self._url = url

    def _load(self):
        rinfo = os.path.join(self.path, "release_info.json")
        version_path = os.path.join(self.path, ".version")

        data = dict()
        if self._url and self._url.startswith('https://github.com/'):
            path = self._url.removeprefix('https://github.com/').split('/', maxsplit=2)
            if len(path) >= 2:
                data.update(project_owner=path[0], project_name=path[1])

        if os.path.exists(rinfo):
            try:
                data.update(json.loads(readfile(rinfo)))
            except Exception:
                logging.exception("Failed to load release_info.json.")
        elif os.path.exists(version_path):
            data.update(version=readfile(version_path).strip())

        return data

    async def refresh(self, lock: Versioned, **kw) -> None:
        data = self._load()
        lock.current_version = data.get('version', '?')
        lock.remote_version = await self._get_remote_version(data)
        lock.commits_behind = []
        lock.refresh_time = time.time()

    async def update(self, lock: Versioned, **kw) -> bool:
        if lock.current_version != '?' and lock.remote_version != '?' and lock.remote_version == lock.current_version:
            return False

        if self._url and self._url.startswith('https://github.com/'):
            data = self._load()
            if repo := self._repo_url_part(data):
                name = data.get('project_name')
                url = f'https://github.com/{repo}/releases/download/{lock.remote_version}/{name}.zip'
                self._extract_zip_file(url, self.path)
                return True

        return False

    async def _get_remote_version(self, data: dict, channel: str = 'stable'):
        if repo := self._repo_url_part(data):
            if channel == 'stable':
                resource = f"repos/{repo}/releases/latest"
            else:
                resource = f"repos/{repo}/releases?per_page=1"

            headers = {"Accept": "application/vnd.github.v3+json"}

            try:
                resp = await get(f'https://api.github.com/{resource}', headers=headers)
            except Exception:
                logging.exception("Failed to load release_info.json.")
            else:
                if resp.status_code in (200, 304) and resp.content:
                    release = resp.json()

                    if isinstance(release, list) and len(release) > 0:
                        release = release[0]

                    if isinstance(release, dict) and (version := release.get('name', None)):
                        return version
        return '?'

    @staticmethod
    def _repo_url_part(data: dict):
        if (owner := data.get('project_owner')) and (name := data.get('project_name')):
            return f"{owner}/{name}"
        return None

    @staticmethod
    def _extract_zip_file(file_path_or_url: str, output: str):
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
            os.makedirs(output, exist_ok=True)
            zip_ref.extractall(output)

            # Delete the temporary file if it was downloaded from a URL
        if file_path_or_url.startswith('http'):
            os.remove(zip_file_name)
