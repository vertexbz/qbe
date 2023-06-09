from __future__ import annotations
import qbe.cli as cli
from qbe.config import Config


@cli.command(short_help='Updates devices via can boot')
@cli.pass_config
def can_update(config: Config):
    pass
