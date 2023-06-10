from __future__ import annotations

import asyncio
import re

from tabulate import tabulate

import qbe.cli as cli
from qbe.support.canboot import create_socket, hijack_output, restore_output

re_device_uuid = r"Detected UUID: ([^,]+), Application: (.+)"


@cli.command(short_help='Lists CanBoot devices')
@cli.option('--interface', '-i', default='can0')
def canboot_list(interface: str):
    loop = asyncio.get_event_loop()
    try:
        sock = create_socket(loop)
    except ModuleNotFoundError as e:
        raise cli.Error(str(e))
    except:
        raise cli.Error('failed acquiring can interface')

    nodes: dict[str, str] = {}

    def hijack_line(msg: str) -> None:
        if msg == 'Resetting all bootloader node IDs...':
            return
        if msg == 'Checking for canboot nodes...':
            return

        matches = re.search(re_device_uuid, msg)
        if matches:
            nodes.update({matches.group(1): matches.group(2)})
            return

        print(msg)

    try:
        hijack_output(hijack_line)
        loop.run_until_complete(sock.run_query(interface))
    except Exception as e:
        raise cli.Error('Can query error: ' + str(e))
    finally:
        restore_output()

    sock.close()

    print(cli.success('Query Complete'))

    if len(nodes.keys()) > 0:
        table = [
            ['UUID', 'Application'],
            *[[uuid, app] for uuid, app in nodes.items()]
        ]
        print(tabulate(table, headers='firstrow', tablefmt='rounded_grid', intfmt=','))
