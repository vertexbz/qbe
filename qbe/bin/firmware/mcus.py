from __future__ import annotations
import qbe.cli as cli
from qbe.config import Config
from qbe.config.mcu import MCUFwStatus


def _fw_status_to_str(status: MCUFwStatus) -> str:
    if status == MCUFwStatus.ABSENT:
        return cli.dim('absent')
    if status == MCUFwStatus.OUTDATED:
        return cli.warning('outdated')
    if status == MCUFwStatus.BUILT:
        return cli.success('ready to update')
    if status == MCUFwStatus.UP_TO_DATE:
        return cli.updated('up to date')

    raise ValueError('unknown status')


@cli.command(short_help='List available mcus')
@cli.option('--long', '-l', is_flag=True, default=False)
@cli.pass_config
def mcus(config: Config, long: bool):
    for mcu in config.mcus:
        print('- ', end='')
        print(cli.bold(mcu.preset))
        print('  Firmware status: ' + _fw_status_to_str(mcu.fw_status))
        [print('  ' + k + ': ' + cli.message_important(v)) for k, v in mcu.info.items()]
        if long:
            print('  config:')
            [print('    ' + cli.message(l)) for l in mcu.render_config().split('\n') if not l.startswith('#')]
        print()
