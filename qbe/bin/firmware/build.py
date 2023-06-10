from __future__ import annotations

import os
import shutil

import qbe.cli as cli
from qbe.config import Config
from qbe.config.mcu import MCUFwStatus
from qbe.support import services, Command


@cli.command(short_help='Builds new version of firmware for every mcu')
@cli.pass_config
def build(config: Config):
    if services.klipper is None:
        raise cli.Error('klipper not found')

    make = Command('/usr/bin/make', cwd=services.klipper.srcdir)
    target_config = os.path.join(services.klipper.srcdir, '.config')
    target_path = os.path.join(services.klipper.srcdir, 'out', 'klipper.bin')

    os.makedirs(config.paths.firmwares, exist_ok=True)

    for mcu in config.mcus:
        if mcu.fw_status not in (MCUFwStatus.ABSENT, MCUFwStatus.OUTDATED):
            print(cli.dim(f'skipping {cli.bold(mcu.fw_file)}{cli.CODE_DIM} - up to date'))
            continue

        print(f'building {cli.bold(mcu.fw_file)}... ', end='', flush=True)

        make.piped(['clean'])

        config_stream = os.open(target_config, os.O_WRONLY)
        os.write(config_stream, mcu.render_config().encode('utf-8'))

        make.piped([])

        shutil.copyfile(target_path, mcu.fw_path)

        print(cli.success('OK'))

    if os.path.exists(target_config):
        os.unlink(target_config)
