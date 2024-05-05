from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from server import Server
    from components.file_manager.file_manager import FileManager


class NoLowerString(str):
    def lower(self):
        return self


def register_directory(server: Server, name: str, path: str, full_access=False) -> None:
    file_manager: FileManager = server.lookup_component('file_manager')
    file_manager.register_directory(name, path, full_access)
    server.register_static_file_handler(name.replace(' ', '%20'), path)


def symlink(src: str, dst_dir: str, hard=False) -> Optional[str]:
    to_link = os.path.expanduser(src)
    if not os.path.exists(to_link):
        return None

    dst = os.path.join(dst_dir, os.path.basename(to_link))
    if os.path.exists(dst):
        return dst

    if hard:
        os.link(to_link, dst)
    else:
        os.symlink(to_link, dst)
    return dst


def is_mcu_key(key: str) -> bool:
    return key == 'mcu' or key.startswith('mcu ')


def format_version(version: str, short=False):
    version = version.strip()

    if short:
        version = re.sub(r'(-g[a-f0-9]{8})$', '', version)

    if re.compile(r'^\d+\.\d+').match(version):
        return f'v{version}'

    return version


def ssh_to_https(url: str):
    if '://' not in url:
        url = url.replace("git@", "https://").replace(":", "/")
    return url

