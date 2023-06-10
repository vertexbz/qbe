from __future__ import annotations
import qbe.cli as cli
from qbe.config import Config


@cli.command(short_help='List available mcus')
@cli.option('--long', '-l', is_flag=True, default=False)
@cli.pass_config
def mcus(config: Config, long: bool):
    for mcu in config.mcus:
        print('- ', end='')
        print(cli.bold(mcu.preset))
        [print('  ' + k + ': ' + cli.message_important(v)) for k, v in mcu.info.items()]
        if long:
            print('  config:')
            [print('    ' + cli.message(l)) for l in mcu.render_config().split('\n') if not l.startswith('#')]
        print()
