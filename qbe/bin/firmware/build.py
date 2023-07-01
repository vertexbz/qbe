from __future__ import annotations

import os
import shutil
from typing import Union

import qbe.cli as cli
from qbe.config import Config
from qbe.config.mcu import BaseMCU
from qbe.config.mcu import MCUFwStatus
from qbe.support import services, Command


def build_firmware(mcu: BaseMCU, verbose=False):
    make = Command('/usr/bin/make', cwd=services.klipper.srcdir)
    target_config = os.path.join(services.klipper.srcdir, '.config')
    target_path = os.path.join(services.klipper.srcdir, 'out', 'klipper.bin')

    make.piped(['clean'])

    config_stream = os.open(target_config, os.O_WRONLY)
    os.write(config_stream, mcu.render_config().encode('utf-8'))

    if verbose:
        make.attached([])
    else:
        make.piped([])

    shutil.copyfile(target_path, mcu.fw_path)

    if os.path.exists(target_config):
        os.unlink(target_config)


@cli.command(short_help='Builds new version of firmware for every mcu')
@cli.argument('name', required=False)
@cli.option('--verbose', '-v', default=False, is_flag=True)
@cli.pass_config
def build(config: Config, name: Union[str, None], verbose: bool):
    if services.klipper is None:
        raise cli.Error('klipper not found')

    mcus = config.mcus[:]
    if name is not None:
        mcus = list(filter(lambda m: m.name.lower() == name.lower(), mcus))
        if len(mcus) == 0:
            raise cli.Error(f'no MCUs matching name {name}')

    os.makedirs(config.paths.firmwares, exist_ok=True)

    for mcu in mcus:
        if mcu.fw_status == MCUFwStatus.NOT_APPLY:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - not apply'))
            continue
        if mcu.fw_status not in (MCUFwStatus.ABSENT, MCUFwStatus.OUTDATED):
            print(cli.dim(f'skipping {cli.bold(mcu.fw_file)}{cli.CODE_DIM} - up to date'))
            continue

        print(f'building {cli.bold(mcu.fw_file)}... ', end='', flush=True)
        if verbose:
            print()

        build_firmware(mcu, verbose)

        if verbose:
            print(cli.success('Done!'))
        else:
            print(cli.success('OK'))
