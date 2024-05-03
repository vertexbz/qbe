from __future__ import annotations

from typing import Optional

import click

from ..cli import async_command
from ..cli.lockfile import pass_lockfile
from ..cli.progress import CliProgress
from ..cli.qbefile import pass_qbefile
from ..lockfile import LockFile
from ..mcu import MCU
from ..qbefile import QBEFile
from ..trigger.service_reload import ServiceReloadTrigger


@async_command(short_help='Update MCU Firmware')
@click.argument('name', required=False)
@click.option('--all', '-a', default=False, is_flag=True)
@click.option('--force', '-f', default=False, is_flag=True)
@click.option('--build-only', '-b', default=False, is_flag=True)
@pass_lockfile
@pass_qbefile
async def mcu_update(qbefile: QBEFile, lockfile: LockFile, name: Optional[str], all: bool, force: bool, build_only: bool) -> None:
    if (all and name) or (not all and not name):
        raise click.BadParameter('Either --all or --name has to be provided')

    if name:
        name = name.lower()

    if name and name not in map(lambda m: m.name.lower(), qbefile.mcus):
        raise click.BadParameter(f'Unknown name {name}')

    progress = CliProgress(lockfile)
    try:
        for mcu_config in qbefile.mcus:
            lock = lockfile.mcus.always(mcu_config.name)
            mcu = MCU(mcu_config, lock)

            if name is not None and mcu.name.lower() != name:
                continue

            if force:
                lock.remote_version = '??'

            with progress.updatable(mcu) as p:
                await mcu.update(progress=p, build_only=build_only)

        triggers = ServiceReloadTrigger.dedupe(progress.triggers)
        for trig, updatable in triggers:
            await trig.handle(progress, updatable)
    finally:
        lockfile.save()
