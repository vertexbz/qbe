from __future__ import annotations

import asyncio

import click
from tabulate import tabulate

from ...cli import async_command, fine, warning
from ...mcu.provider.flash.canboot.socket import CanSocket


@async_command(short_help='Lists CanBoot devices')
@click.option('--interface', '-i', default='can0')
async def canboot_list(interface: str):
    with CanSocket(asyncio.get_event_loop(), interface) as sock:
        results = await sock.query()

    fine('Query Complete')
    print()

    if len(results) == 0:
        warning('No Can nodes found')
        return

    table = [
        ['', 'UUID', 'Application'],
    ]

    for i, (uuid, app) in enumerate(results, start=1):
        table.append([i, uuid, app])

    print(tabulate(table, headers='firstrow', tablefmt='rounded_grid', intfmt=','))
