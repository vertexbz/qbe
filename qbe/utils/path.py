from __future__ import annotations

import os


def pop_expand(kw: dict, key: str, default=None):
    path = kw.pop(key, default)
    if path is None:
        return path

    return os.path.expanduser(path)
