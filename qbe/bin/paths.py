from __future__ import annotations
import pprint
import qbe.cli as cli
from qbe.config import Config


@cli.command(short_help='Display paths')
@cli.pass_config
def paths(config: Config):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config.paths.__dict__)
