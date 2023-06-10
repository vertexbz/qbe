from __future__ import annotations
import psutil
from tabulate import tabulate
import qbe.cli as cli


def intfmt(val: int) -> str:
    return format(val, ',')


@cli.command(short_help='Display can stats')
def can_stats():
    stats = {k: v for k, v in psutil.net_io_counters(pernic=True).items() if k.startswith('can')}

    if len(stats.keys()) == 0:
        raise cli.Error('No can interfaces found!')

    for iface, s in stats.items():
        table = [
            [cli.bold(iface), 'Bytes', 'Packets', cli.error('Errors'), cli.error('Dropped')],
            ['Received', intfmt(s.bytes_recv), intfmt(s.packets_recv),
             cli.error(intfmt(s.errin)) if s.errin > 0 else '0',
             cli.error(intfmt(s.dropin)) if s.dropin > 0 else '0',
             ],
            ['Sent', intfmt(s.bytes_sent), intfmt(s.packets_sent),
             cli.error(intfmt(s.errout)) if s.errout > 0 else '0',
             cli.error(intfmt(s.dropout)) if s.dropout > 0 else '0'
             ]
        ]
        print(tabulate(table, headers='firstrow', tablefmt='rounded_grid',
                       colalign=('left', 'right', 'right', 'right', 'right')))
