from __future__ import annotations
import qbe.cli as cli
from qbe.config import Config


def _print(paths: dict, indent=0):
    for k, v in paths.items():
        if isinstance(v, dict):
            print('  ' * indent + k + ':')
            _print(v, indent=indent + 1)
        else:
            print('  ' * indent + k + ': ' + cli.message_important(v))


@cli.command(short_help='Display paths')
@cli.pass_config
def paths(config: Config):
    print('config.paths:')
    _print(config.paths.__dict__, indent=1)
