from __future__ import annotations
import qbe.cli as cli
from qbe.config import Config


@cli.command(short_help='Display paths')
@cli.pass_config
def paths(config: Config):
    print('config.paths:')
    cli.dict_print(config.paths.__dict__, indent=1)
