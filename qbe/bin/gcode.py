from __future__ import annotations
import qbe.cli as cli
from qbe.support import services


@cli.command(short_help='Run gcode')
@cli.argument('gcode', nargs=-1)
def gcode(gcode: list[str]):
    if services.klipper is None:
        raise cli.Error('klipper not found')

    if len(gcode) == 0:
        raise cli.Error('provide gcode to run')

    services.klipper.gcode(' '.join(gcode))
