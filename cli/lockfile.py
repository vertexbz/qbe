from __future__ import annotations

from functools import update_wrapper
from typing import Any, Callable, TypeVar, cast, Optional

import click

from ..lockfile import LockFile
from ..lockfile.utils import for_qbe_file

F = TypeVar('F', bound=Callable[..., Any])


def init_lockfile_context(ctx: click.Context, path: Optional[str]):
    if not ctx.obj:
        ctx.obj = {}

    ctx.obj['lockfile'] = LockFile.load(path or for_qbe_file(ctx.obj['qbefile']))


def pass_lockfile(f: F) -> F:
    def new_func(*args, **kwargs):  # type: ignore
        return f(click.get_current_context().obj['lockfile'], *args, **kwargs)

    return update_wrapper(cast(F, new_func), f)
