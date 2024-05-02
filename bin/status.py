from __future__ import annotations

from typing import TYPE_CHECKING

import click
from tabulate import tabulate

from ..cli import async_command
from ..cli.color import tokenbased_randomcolorpool, name_color
from ..cli.lockfile import pass_lockfile
from ..cli.qbefile import pass_qbefile
from ..lockfile import LockFile
from ..mcu import MCU
from ..package import build as build_package
from ..package.qbe import QBE as QBEPackage
from ..qbefile.dependency import from_lock

if TYPE_CHECKING:
    from ..qbefile import QBEFile
    from ..updatable.identifier import Identifier


@async_command(short_help='Packages status')
@pass_lockfile
@pass_qbefile
async def status(qbefile: QBEFile, lockfile: LockFile) -> None:
    type_color = tokenbased_randomcolorpool(78564765489)

    table = [
        [
            '',
            click.style('Name', bold=True),
            click.style('Type', bold=True),
            click.style('ID', bold=True),
            click.style('Current version', bold=True),
            ''
        ]
    ]

    processed_identifiers = set()
    for i, pkg in enumerate(pkgs(qbefile, lockfile), start=1):
        if isinstance(pkg, QBEPackage):
            row = [i, click.style(pkg.name, fg=name_color(pkg.name)), '', 'QBE']
        elif isinstance(pkg, MCU):
            row = [i, f'MCU {click.style(pkg.name, fg=name_color(pkg.name))}', '', '']
        else:
            processed_identifiers.add(pkg.identifier)
            row = [
                i,
                click.style(pkg.name, fg=name_color(pkg.name)),
                click.style(pkg.identifier.type, fg=type_color(pkg.identifier.type), dim=True),
                pkg.identifier.id
            ]

        if pkg.version.local == pkg.version.remote:
            row.append(click.style(pkg.version.local, fg='green'))
            row.append(click.style('up to date', dim=True))
        elif pkg.version.local == f'{pkg.version.remote}-dirty':
            row.append(click.style(pkg.version.local, fg='yellow', dim=True))
            row.append('local changes detected')
        elif pkg.version.local.endswith('-dirty'):
            row.append(click.style(pkg.version.local, fg='yellow'))
            row.append(f'local changes detected, update available ({click.style(pkg.version.remote, fg="green")})')
        elif pkg.version.local == '?' and pkg.version.remote == '?':
            row.append(click.style(pkg.version.local, dim=True))
            row.append(click.style(f'unknown', fg='yellow'))
        elif pkg.version.local == '?':
            row.append(click.style(pkg.version.local, dim=True))
            row.append(f'will be installed ({click.style(pkg.version.remote, fg="green")})')
        elif pkg.version.remote == '?':
            row.append(click.style(pkg.version.local, fg='green'))
            row.append(click.style(f'unknown remote version', fg='yellow'))
        else:
            row.append(pkg.version.local)
            row.append(f'update available ({click.style(pkg.version.remote, fg="green")})')

        table.append(row)

    for i, pkg in enumerate(removed_pkgs(lockfile, processed_identifiers), start=len(table)):
        table.append([
            i,
            click.style(pkg.name, fg=name_color(pkg.name)),
            click.style(pkg.identifier.type, fg=type_color(pkg.identifier.type), dim=True),
            pkg.identifier.id,
            click.style(pkg.version.local, dim=True),
            click.style(f'will be removed', fg='bright_red')
        ])

    print(tabulate(table, headers='firstrow', tablefmt='rounded_grid', colalign=('right', 'left', 'right', 'left', 'left', 'left')))


def pkgs(qbefile: QBEFile, lockfile: LockFile):
    yield QBEPackage(lockfile.qbe)

    for dep in qbefile.requires:
        lock = lockfile.requires.always(dep.identifier)
        yield build_package(dep, lock)

    for mcu_config in qbefile.mcus:
        lock = lockfile.mcus.always(mcu_config.name)
        yield MCU(mcu_config, lock)


def removed_pkgs(lockfile: LockFile, processed_identifiers: set[Identifier]):
    for identifier, lock in lockfile.requires.difference(processed_identifiers).items():
        yield build_package(from_lock(identifier, lock), lock)
