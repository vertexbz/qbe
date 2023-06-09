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
            [cli.bold(iface), 'Bytes', 'Packets', 'Errors', 'Dropped'],
            ['Received', s.bytes_recv, s.packets_recv, s.errin, s.dropin],
            ['Sent', s.bytes_sent, s.packets_sent, s.errout, s.dropout]
        ]
        print(tabulate(table, headers='firstrow', tablefmt='rounded_grid', intfmt=','))
