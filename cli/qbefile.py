from __future__ import annotations

from functools import update_wrapper
import os
from typing import Any, Callable, TypeVar, cast, Optional

import click

from ..paths import paths
from ..qbefile import load, QBEFile
from ..qbefile.utils import find_in, CONFIG_FILE_NAMES

F = TypeVar('F', bound=Callable[..., Any])


def init_qbefile_context(ctx: click.Context, path: Optional[str]):
    if not ctx.obj:
        ctx.obj = {}

    ctx.obj['qbefile'] = load(path) if os.path.isfile(path) else QBEFile(path)


def pass_qbefile(f: F) -> F:
    def new_func(*args, **kwargs):  # type: ignore
        return f(click.get_current_context().obj['qbefile'], *args, **kwargs)

    return update_wrapper(cast(F, new_func), f)


def get_default_qbefile_path() -> str:
    try:
        return find_in(paths.config_root)
    except:
        pass

    return os.path.join(paths.config_root, CONFIG_FILE_NAMES[0])
