from __future__ import annotations

from typing import Union

import qbe.cli as cli
from qbe.config import Config


@cli.command(short_help='Deploys bootloader updater')
@cli.argument('name', required=False)
@cli.option('--all', '-a', is_flag=True, default=False)
@cli.pass_config
def deploy(config: Config, name: Union[str, None], all: bool):
    if name is None and not all:
        raise cli.Error('you have to either specify a name of mcu or provide --all/-a option o update all')
