from __future__ import annotations

import os
from typing import Union

import qbe.cli as cli
from qbe.config import Config
from qbe.firmware import MCUFwStatus


@cli.command(short_help='Deploys bootloader updater')
@cli.argument('name', required=False)
@cli.option('--all', '-a', is_flag=True, default=False)
@cli.pass_config
def deploy(config: Config, name: Union[str, None], all: bool):
    if name is None and not all:
        raise cli.Error('you have to either specify a name of mcu or provide --all/-a option o update all')

    canboot_dir = os.path.join(config.paths.packages, 'canboot')
    if not os.path.isdir(canboot_dir):
        raise cli.Error('canboot not found')

    mcus = config.mcus[:]
    if name is not None:
        mcus = list(filter(lambda m: m.name.lower() == name.lower() and m.bootloader is not None, mcus))
        if len(mcus) == 0:
            raise cli.Error(f'no MCUs matching name {name}')

    os.makedirs(config.paths.firmwares, exist_ok=True)

    for mcu in mcus:
        deployer = mcu.bootloader.with_options(deployer=True)

        if deployer is None or deployer.status == MCUFwStatus.NOT_APPLY:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - not apply'))
            continue
        if deployer.status not in (MCUFwStatus.ABSENT, MCUFwStatus.OUTDATED):
            print(cli.dim(f'skipping {cli.bold(deployer.filename)}{cli.CODE_DIM} - up to date'))
            continue

        if deployer.status != MCUFwStatus.BUILT:
            print(f'building {cli.bold(deployer.filename)}... ', end='', flush=True)
            deployer.build()  # TODO temp file?

        if deployer.status != MCUFwStatus.BUILT:
            print(cli.error(f'Failed building {cli.bold(deployer.name)}{cli.CODE_DIM} firmware!'))
            continue

        # TODO can upload

        print(cli.success('OK'))
