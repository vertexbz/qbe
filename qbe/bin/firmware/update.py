from __future__ import annotations

import time
import os
from typing import Union

import qbe.cli as cli
from qbe.config import Config
from qbe.config.mcu import CanMCU
from qbe.firmware import MCUFwStatus
from qbe.firmware import flash
from qbe.support import services


@cli.command(short_help='Updates MCU(s)')
@cli.argument('name', required=False)
@cli.option('--all', '-a', is_flag=True, default=False)
@cli.pass_config
def update(config: Config, name: Union[str, None], all: bool):
    if name is None and not all:
        raise cli.Error('you have to either specify a name of mcu or provide --all/-a option o update all')

    if services.klipper is None:
        raise cli.Error('klipper not found')

    mcus = config.mcus[:]
    mcus = list(filter(lambda m: isinstance(m, CanMCU), mcus))
    if name is not None:
        mcus = list(filter(lambda m: m.name.lower() == name.lower(), mcus))
        if len(mcus) == 0:
            raise cli.Error(f'no MCUs matching name {name}')

    os.makedirs(config.paths.firmwares, exist_ok=True)

    for mcu in mcus:
        if mcu.firmware.status == MCUFwStatus.NOT_APPLY:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - not apply'))
            continue
        if mcu.firmware.status == MCUFwStatus.UP_TO_DATE:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - up to date'))
            continue

        line = cli.Line()
        line.print(f'Updating MCU {cli.bold(mcu.name)}...')
        time.sleep(0.25)

        if mcu.firmware.status != MCUFwStatus.BUILT:
            line.print(f'Building {cli.bold(mcu.name)} firmware...')
            mcu.firmware.build()

        if mcu.firmware.status != MCUFwStatus.BUILT:
            line.finish()
            print(cli.error(f'Failed building {cli.bold(mcu.firmware.name)}{cli.CODE_DIM} firmware!'))
            continue

        line.print(f'Flashing {cli.bold(mcu.name)} firmware...')

        try:
            if mcu.config.bootloader_type is not None:
                flash(config, mcu, mcu.config.bootloader_type, mcu.firmware.path)
            else:
                flash(config, mcu, mcu.flash_mode, mcu.firmware.path)  # TODO let the user choose
        except Exception as e:
            line.finish()
            cli.error_with_trace(e, prefix='Flash error')
            continue

        line.print(cli.updated('MCU ') + cli.updated(cli.bold(mcu.name)) + cli.updated(' updated!'))
        line.finish()
