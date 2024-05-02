from __future__ import annotations

import click
import psutil
from tabulate import tabulate

from ...cli import error, bold


def intfmt(val: int) -> str:
    return format(val, ',')


@click.command(short_help='Display can stats')
def can_stats():
    stats = {k: v for k, v in psutil.net_io_counters(pernic=True).items() if k.startswith('can')}

    if len(stats.keys()) == 0:
        error('No can interfaces found!')

    for iface, s in stats.items():
        table = [
            [bold(iface), 'Bytes', 'Packets', error('Errors'), error('Dropped')],
            ['Received', intfmt(s.bytes_recv), intfmt(s.packets_recv),
             error(intfmt(s.errin)) if s.errin > 0 else '0',
             error(intfmt(s.dropin)) if s.dropin > 0 else '0',
             ],
            ['Sent', intfmt(s.bytes_sent), intfmt(s.packets_sent),
             error(intfmt(s.errout)) if s.errout > 0 else '0',
             error(intfmt(s.dropout)) if s.dropout > 0 else '0'
             ]
        ]
        print(tabulate(table, headers='firstrow', tablefmt='rounded_grid',
                       colalign=('left', 'right', 'right', 'right', 'right')))
