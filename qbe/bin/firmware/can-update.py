from __future__ import annotations

import asyncio
import pathlib
import time
import os
from typing import Union

import qbe.cli as cli
from qbe.config import Config
from qbe.config.mcu import CanMCU
from qbe.config.mcu import MCUFwStatus
from qbe.support import services
import qbe.support.canboot as canboot
from .build import build_firmware

output_line = canboot.output_line


def hijack_line(msg: str) -> None:
    print('H: ' + msg)


@cli.command(short_help='Updates devices via can boot')
@cli.argument('name', required=False)
@cli.option('--all', '-a', is_flag=True, default=False)
@cli.pass_config
def can_update(config: Config, name: Union[str, None], all: bool):
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

    loop = asyncio.get_event_loop()
    try:
        sock = canboot.CanSocket(loop)
    except:
        raise cli.Error('failed acquiring can interface')

    os.makedirs(config.paths.firmwares, exist_ok=True)

    for mcu in mcus:
        if mcu.fw_status == MCUFwStatus.UP_TO_DATE:
            print(cli.dim(f'skipping {cli.bold(mcu.name)}{cli.CODE_DIM} - up to date'))
            continue

        line = cli.Line()
        line.print(f'Updating MCU {cli.bold(mcu.name)}...')
        time.sleep(0.25)

        if mcu.fw_status != MCUFwStatus.BUILT:
            line.print(f'Building {cli.bold(mcu.name)} firmware...')
            build_firmware(mcu)

        if mcu.fw_status != MCUFwStatus.BUILT:
            line.finish()
            print(cli.error(f'Failed building {cli.bold(mcu.fw_name)}{cli.CODE_DIM} firmware!'))
            continue

        line.print(f'Flashing {cli.bold(mcu.name)} firmware...')

        try:
            canboot.output_line = hijack_line
            loop.run_until_complete(sock.run(mcu.interface, int(mcu.can_id, 16), pathlib.Path(mcu.fw_path), False))
        except Exception as e:
            line.finish()
            print(cli.error('CAN flash error: ') + cli.error(str(e)))
            continue
        finally:
            canboot.output_line = output_line

        line.print(cli.updated('MCU ') + cli.updated(cli.bold(mcu.name)) + cli.updated(' updated!'))

    sock.close()
