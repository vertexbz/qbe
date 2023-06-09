from __future__ import annotations

import os
import shutil

import qbe.cli as cli
from qbe.config import Config
from qbe.support import services, Command


@cli.command(short_help='Builds new version of firmware for every mcu')
@cli.pass_config
def build(config: Config):
    if services.klipper is None:
        raise cli.Error('klipper not found')

    make = Command('/usr/bin/make', cwd=services.klipper.srcdir)
    klipper_head = os.path.join(services.klipper.srcdir, '.git', 'FETCH_HEAD')
    target_config = os.path.join(services.klipper.srcdir, '.config')
    target_path = os.path.join(services.klipper.srcdir, 'out', 'klipper.bin')
    build_firmwares_dir = os.path.join(config.paths.moonraker.data, 'firmware')

    os.makedirs(build_firmwares_dir, exist_ok=True)

    for mcu in config.mcus:
        fw_file = mcu.fw_name + '.bin'
        firmware_path = os.path.join(build_firmwares_dir, fw_file)

        if os.path.exists(firmware_path) and os.path.getmtime(firmware_path) > os.path.getmtime(klipper_head):
            print(cli.dim(f'skipping {cli.bold(fw_file)}{cli.CODE_DIM} - up to date'))
            continue

        print(f'building {cli.bold(fw_file)}... ', end='', flush=True)

        make.piped(['clean'])

        config_stream = os.open(target_config, os.O_WRONLY)
        os.write(config_stream, mcu.render_config().encode('utf-8'))

        make.piped([])

        shutil.copyfile(target_path, firmware_path)

        print(cli.success('OK'))

    if os.path.exists(target_config):
        os.unlink(target_config)
