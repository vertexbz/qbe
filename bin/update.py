from __future__ import annotations

from typing import Optional

import click

from ..cli import async_command
from ..cli.lockfile import pass_lockfile
from ..cli.progress import CliProgress
from ..cli.qbefile import pass_qbefile
from ..lockfile import LockFile
from ..package import build as build_package
from ..qbefile import QBEFile
from ..qbefile.dependency import from_lock
from ..trigger.service_reload import ServiceReloadTrigger


@async_command(short_help='Update dependencies')
@click.argument('name', required=False)
@click.option('--remove-only', '-r', default=False, is_flag=True)
@pass_lockfile
@pass_qbefile
async def update(qbefile: QBEFile, lockfile: LockFile, name: Optional[str], remove_only: bool) -> None:
    with CliProgress(lockfile) as progress:
        processed_identifiers = set()
        try:
            for dep in qbefile.requires:
                processed_identifiers.add(dep.identifier)
                if remove_only:
                    continue

                pkg = build_package(dep, lockfile.requires.always(dep.identifier))
                if name is not None and pkg.name != name:
                    continue

                with progress.updatable(pkg) as p:
                    await pkg.update(progress=p)

            for identifier, lock in lockfile.requires.difference(processed_identifiers).items():
                pkg = build_package(from_lock(identifier, lock), lock)
                if name is not None and pkg.name != name:
                    continue

                with progress.updatable(pkg) as p:
                    await pkg.remove(progress=p)

            triggers = ServiceReloadTrigger.dedupe(progress.triggers)
            for trig, updatable in triggers:
                await trig.handle(progress, updatable)
        finally:
            installed = progress.stats_installed
            updated = progress.stats_updated
            removed = progress.stats_removed
            unchanged = progress.stats_total - (installed + updated + removed)

            print()
            print(''.join([
                '[',
                cs('Installed', installed > 0, {'fg': 'bright_green'}, {}), ' ',
                cs(str(installed), installed > 0, {'fg': 'bright_green'}, {'dim': True}),
                '] ',
                '[',
                cs('Updated', updated > 0, {'fg': 'green'}, {}), ' ',
                cs(str(updated), updated > 0, {'fg': 'green'}, {'dim': True}),
                '] ',
                '[',
                cs('Removed', removed > 0, {'fg': 'red'}, {}), ' ',
                cs(str(removed), removed > 0, {'fg': 'red'}, {'dim': True}),
                '] ',
                '[',
                cs('Unchanged', unchanged > 0, {'fg': 'blue'}, {}), ' ',
                cs(str(unchanged), unchanged > 0, {'fg': 'blue'}, {'dim': True}),
                ']'
            ]))


def cs(message: str, condition: bool, true_style: dict, false_style: dict) -> str:
    if condition:
        if not true_style:
            return message
        return click.style(message, **true_style)

    if not false_style:
        return message
    return click.style(message, **false_style)
