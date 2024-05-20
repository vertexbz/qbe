from __future__ import annotations

import re


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

