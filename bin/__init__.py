from __future__ import annotations

import importlib
from inspect import getmembers
import pkgutil
from typing import Optional

import click

from ..cli.lockfile import init_lockfile_context
from ..cli.qbefile import get_default_qbefile_path, init_qbefile_context

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--config', default=get_default_qbefile_path)
@click.option('-l', '--lockfile', default=None)
@click.pass_context
def entry(ctx: click.Context, config: str, lockfile: Optional[str]):
    init_qbefile_context(ctx, config)
    init_lockfile_context(ctx, lockfile)


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    im = importlib.import_module(module)
    for _, command in getmembers(im, lambda x: isinstance(x, (click.Command, click.Group))):
        entry.add_command(command)
