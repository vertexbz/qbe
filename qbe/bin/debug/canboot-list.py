from __future__ import annotations

import asyncio

import qbe.cli as cli
import qbe.support.canboot as canboot


def hijack_line(msg: str) -> None:
    print('H: ' + msg)


@cli.command(short_help='Lists CanBoot devices')
@cli.option('--interface', '-i', default='can0')
def canboot_list(interface: str):
    loop = asyncio.get_event_loop()
    try:
        sock = canboot.CanSocket(loop)
        canboot.output_line = hijack_line
    except:
        raise cli.Error('failed acquiring can interface')

    try:
        loop.run_until_complete(sock.run_query(interface))
    except Exception as e:
        raise cli.Error('Can query error: ' + str(e))

    sock.close()

    print(cli.success('Query Complete'))
