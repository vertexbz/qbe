from __future__ import annotations

from typing import Optional

import click

from ..cli import async_command, warning, fine, comment
from ..cli.color import name_color
from ..cli.lockfile import pass_lockfile
from ..cli.progress import CliProgress
from ..cli.qbefile import pass_qbefile
from ..lockfile import LockFile
from ..mcu import MCU
from ..package import build as build_package
from ..package.qbe import QBE as QBEPackage
from ..qbefile import QBEFile


@async_command(short_help='Refresh remotes')
@click.argument('name', required=False)
@click.option('--mcus-only', '-m', default=False, is_flag=True)
@pass_lockfile
@pass_qbefile
async def refresh(qbefile: QBEFile, lockfile: LockFile, name: Optional[str], mcus_only: bool) -> None:
    with CliProgress(lockfile) as progress:
        if not mcus_only:
            for lock, pkg in packages(qbefile, lockfile):
                if name is not None and pkg.name != name:
                    continue

                if lock.status.unfinished():
                    print(progress.formatter.format_updatable(pkg) + ' ' + warning('update unfinished, skipping'))
                    continue

                with progress.updatable(pkg) as p:
                    await pkg.refresh(progress=p)

                    if lock.remote_version != lock.current_version.replace('-dirty', ''):
                        p.log(fine(f'current version {lock.current_version}, update available to {lock.remote_version}'))
                    else:
                        p.log(comment('up to date'))

        if not name:
            for mcu_config in qbefile.mcus:
                lock = lockfile.mcus.always(mcu_config.name)
                mcu = MCU(mcu_config, lock)

                if lock.status.unfinished():
                    print(progress.formatter.format_updatable(mcu) + ' ' + warning('update unfinished, skipping'))
                    continue

                with progress.updatable(mcu) as p:
                    await mcu.refresh(progress=p)

                    if lock.remote_version != lock.current_version:
                        p.log(fine(f'current version {lock.current_version}, update available to {lock.remote_version}'))
                    else:
                        p.log(comment('up to date'))


def packages(qbefile: QBEFile, lockfile: LockFile):
    yield lockfile.qbe, QBEPackage(lockfile.qbe)

    for dep in qbefile.requires:
        lock = lockfile.requires.always(dep.identifier)
        pkg = build_package(dep, lock)
        yield lock, pkg


def nc(name: str, mcu=False):
    color = name_color(name)
    if mcu:
        return '[MCU ' + click.style(f'{name}', fg=color) + ']'
    return click.style(f'[{name}]', fg=color)
