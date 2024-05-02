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
                    click.echo(click.style('Error in subcommand occurred!', fg='bright_red', bold=True), err=True)
                    click.echo(click.style(f'Command: {exc_value.command}', fg='bright_red'), err=True)
                    click.echo(click.style(f'Workdir: {exc_value.cwd}', fg='bright_red'), err=True)
                    click.echo(click.style(f'Environment: {exc_value.env}', fg='bright_red'), err=True)
                    click.echo(click.style(f'Stderr:\n{exc_value}', fg='bright_red'), err=True)
                    sys.exit(2)

                click.echo(click.style('Unexpected error occurred!', fg='bright_red', bold=True), err=True)
                click.echo(click.style('Traceback (most recent call last):', fg='bright_red'), err=True)
                formatted_traceback = traceback.format_list(traceback.extract_tb(exc_traceback)[2:])
                click.echo(click.style(''.join(formatted_traceback), fg='bright_red'), nl=False, err=True)
                click.echo(click.style(f'{exc_type.__name__}: {exc_value}', fg='bright_red'), err=True)
                sys.exit(1)

        wrapper.__name__ = f.__name__
        wrapper.__doc__ = f.__doc__

        if hasattr(f, '__click_params__'):
            setattr(wrapper, '__click_params__', f.__click_params__)

        return click.command(*args, **kwargs)(wrapper)

    return decorator


def warning(message: str):
    print(click.style(message, fg='bright_yellow'))


def error(message: str):
    click.echo(click.style(message, fg='bright_red'), err=True)


def fine(message: str):
    print(click.style(message, fg='green'))


def comment(message: str):
    print(click.style(message, dim=True))


def bold(message: str):
    print(click.style(message, bold=True))
