from __future__ import annotations

import click

from ..cli import async_command
from ..cli.lockfile import pass_lockfile
from ..cli.progress import CliProgress
from ..lockfile import LockFile
from ..package.qbe import QBE as QBEPackage


@async_command(short_help='QBE Self Update')
@click.option('--no-refresh', '-r', 'refresh', default=True, is_flag=True)
@pass_lockfile
async def self_update(lockfile: LockFile, refresh: bool) -> None:
    with CliProgress(lockfile) as progress:
        pkg = QBEPackage(lockfile.qbe)

        with progress.updatable(pkg) as p:
            if refresh is True:
                await pkg.refresh(progress=p)
            await pkg.update(progress=p)

        for trig, updatable in progress.triggers:
            await trig.handle(progress, updatable)
