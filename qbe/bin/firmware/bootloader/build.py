from __future__ import annotations

import os
from typing import Union

import qbe.cli as cli
from qbe.config import Config
from qbe.firmware import MCUFwStatus


@cli.command(short_help='Builds new version of firmware for every mcu')
@cli.argument('name', required=False)
@cli.option('--verbose', '-v', default=False, is_flag=True)
@cli.pass_config
def build(config: Config, name: Union[str, None], verbose: bool):
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
        if mcu.bootloader is None or mcu.bootloader.status == MCUFwStatus.NOT_APPLY:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - not apply'))
            continue
        if mcu.bootloader.status not in (MCUFwStatus.ABSENT, MCUFwStatus.OUTDATED):
            print(cli.dim(f'skipping {cli.bold(mcu.bootloader.filename)}{cli.CODE_DIM} - up to date'))
            continue

        print(f'building {cli.bold(mcu.bootloader.filename)}... ', end='', flush=True)
        if verbose:
            print()

        mcu.bootloader.build(verbose)

        if verbose:
            print(cli.success('Done!'))
        else:
            print(cli.success('OK'))
