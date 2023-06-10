from __future__ import annotations
import psutil
from tabulate import tabulate
import qbe.cli as cli


@cli.command(short_help='Display can stats')
def can_stats():
    stats = {k: v for k, v in psutil.net_io_counters(pernic=True).items() if k.startswith('can')}

    if len(stats.keys()) == 0:
        raise cli.Error('No can interfaces found!')

    for iface, s in stats.items():
        table = [
            [cli.bold(iface), 'Bytes', 'Packets', cli.error('Errors'), cli.error('Dropped')],
            ['Received', s.bytes_recv, s.packets_recv,
             cli.error(s.errin) if s.errin > 0 else s.errin,
             cli.error(s.dropin) if s.dropin > 0 else s.dropin,
             ],
            ['Sent', s.bytes_sent, s.packets_sent,
             cli.error(s.errout) if s.errout > 0 else s.errout,
             cli.error(s.dropout) if s.dropout > 0 else s.dropout
             ]
        ]
        print(tabulate(table, headers='firstrow', tablefmt='rounded_grid', intfmt=','))
