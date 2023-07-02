from __future__ import annotations

import os
import sys


def pop_expand(kw: dict, key: str, default=None):
    path = kw.pop(key, default)
    if path is None:
        return path

    return os.path.expanduser(path)


qbedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
qbeenv = os.environ['VIRTUAL_ENV'] if 'VIRTUAL_ENV' in os.environ else os.path.dirname(os.path.dirname(sys.executable))

__all__ = ['qbeenv', 'qbedir', 'pop_expand']
