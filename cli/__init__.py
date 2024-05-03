from __future__ import annotations

import asyncio
import sys
import traceback

import click

from ..adapter.command import CommandError


def async_command(*args, **kwargs):
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(f(*args, **kwargs))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()

                if isinstance(exc_value, CommandError):
                    print_error('Error in subcommand occurred!', bold=True)
                    print_error(f'Command: {exc_value.command}')
                    print_error(f'Workdir: {exc_value.cwd}')
                    print_error(f'Environment: {exc_value.env}')
                    print_error(f'Stderr:\n{exc_value}')
                    sys.exit(2)

                print_error('Unexpected error occurred!', bold=True)
                print_error('Traceback (most recent call last):')
                print_error(''.join(traceback.format_list(traceback.extract_tb(exc_traceback)[2:])), nl=False)
                print_error(f'{exc_type.__name__}: {exc_value}')
                sys.exit(1)

        wrapper.__name__ = f.__name__
        wrapper.__doc__ = f.__doc__

        if hasattr(f, '__click_params__'):
            setattr(wrapper, '__click_params__', f.__click_params__)

        return click.command(*args, **kwargs)(wrapper)

    return decorator


def print_error(message: str, bold=False, nl=True):
    click.echo(error(message, bold=bold), nl=nl, err=True)


def warning(message: str):
    return click.style(message, fg='bright_yellow')


def error(message: str, bold=False):
    return click.style(message, fg='bright_red', bold=bold)


def fine(message: str):
    return click.style(message, fg='green')


def comment(message: str):
    return click.style(message, dim=True)


def bold(message: str):
    return click.style(message, bold=True)
