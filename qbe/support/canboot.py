from __future__ import annotations
import os
import asyncio
import typing


def _canboot_check():
    return os.path.exists(os.path.join(os.path.dirname(__file__), '_canboot.py'))


def hijack_output(fn: typing.Callable[[str], None]):
    if _canboot_check():
        import qbe.support._canboot as canboot
        if hijack_output.output_line is None:
            hijack_output.output_line = canboot.output_line
        canboot.output_line = fn


hijack_output.output_line = None


def restore_output():
    if _canboot_check() and hijack_output.output_line is not None:
        import qbe.support._canboot as canboot
        canboot.output_line = hijack_output.output_line


def create_socket(loop: asyncio.AbstractEventLoop):
    if _canboot_check():
        import qbe.support._canboot as canboot
        return canboot.CanSocket(loop)

    raise ModuleNotFoundError('cannot find canboot package')
