from __future__ import annotations

import asyncio

import click

from ...cli import async_command, fine
from ...mcu.provider.flash.canboot.socket import CanSocket


@async_command(short_help='Reset CanBoot device to bootloader')
@click.option('--interface', '-i', default='can0')
@click.argument('uuid', required=True)
async def canboot_reset(interface: str, uuid: str):
    print(f'Resetting {uuid}...')
    with CanSocket(asyncio.get_event_loop(), interface) as sock:
        await sock.bootloader(int(uuid, 16))

    print(fine('Reset complete'))
