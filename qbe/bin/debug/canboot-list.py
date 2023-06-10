from __future__ import annotations

import asyncio

import qbe.cli as cli
from qbe.support.canboot import CanSocket


@cli.command(short_help='Lists CanBoot devices')
@cli.option('--interface', '-i', default='can0')
def canboot_list(interface: str):
    loop = asyncio.get_event_loop()
    sock = None
    try:
        sock = CanSocket(loop)
        loop.run_until_complete(sock.run_query(interface))
    except Exception:
        raise cli.Error('Can query error')
    finally:
        if sock is not None:
            sock.close()

    print(cli.success('Query Complete'))
