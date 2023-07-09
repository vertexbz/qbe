import os
import traceback
import typing as t
from functools import update_wrapper
import click
from click._compat import term_len


class Error(click.ClickException):
    def show(self, file=None) -> None:
        echo(click.style(f'Error: {self.format_message()}', fg='red'), err=True)


# pylint: disable-next=invalid-name
def echo(msg=None, nl: bool = True, err: bool = False):
    click.echo(msg, nl=nl, err=err)


def bold(text: str) -> str:
    return ''.join([
        click.style(text, bold=True, reset=False),
        click.style('', bold=False, reset=False)
    ])


CODE_DIM = click.style('', dim=True, reset=False)


def dim(text: str) -> str:
    return ''.join([
        click.style(text, dim=True, reset=False),
        click.style('', dim=False, reset=False)
    ])


def success(text: str) -> str:
    return click.style(text, fg='green', dim=True, reset=True)


def warning(text: str) -> str:
    return click.style(text, fg='yellow', reset=True)


def message(text: str) -> str:
    return click.style(text, fg='blue', dim=True, reset=True)


def message_important(text: str) -> str:
    return click.style(text, fg='blue', dim=False, reset=True)


def message_content(text: str) -> str:
    return click.style(text, dim=False, reset=True)


def updated(text: str) -> str:
    return click.style(text, fg='green', reset=True)


def error(text: str) -> str:
    return click.style(text, fg='red', reset=True)


def error_with_trace(err: Exception, prefix: t.Union[None, str] = None):
    msg = "".join(traceback.format_exception(type(err), err, err.__traceback__))
    if prefix is not None:
        print(error(prefix + '! ') + error(msg))
    else:
        print(error(msg))


if os.name == 'nt':
    BEFORE_BAR = '\r'
    AFTER_BAR = '\n'
else:
    BEFORE_BAR = '\r\033[?25l'
    AFTER_BAR = '\033[?25h\n'


class Line:
    def __init__(self, **kwargs) -> None:
        self.max_width = 0
        self.prefix = kwargs.pop('prefix', '')
        self.suffix = kwargs.pop('suffix', '')

    def clear_line(self) -> None:
        buf: list[str] = []
        buf.append(BEFORE_BAR)
        buf.append(' ' * self.max_width)
        click.echo(''.join(buf), nl=False)

    def print(self, line: str, prefix=True, suffix=True, fillup=True) -> None:
        out = ''
        if prefix:
            out = out + self.prefix
        out = out + line
        if suffix:
            out = out + self.suffix

        line_length = term_len(out)
        if line_length > self.max_width:
            self.max_width = line_length

        buf: list[str] = []
        buf.append(BEFORE_BAR)
        buf.append(out)
        if fillup:
            buf.append(' ' * (self.max_width - line_length))

        click.echo(''.join(buf), nl=False)

    def finish(self) -> None:
        click.echo(AFTER_BAR, nl=False)

    def pre_error(self) -> None:
        self.print('', suffix=False)
        self.print('', suffix=False, fillup=False)


F = t.TypeVar('F', bound=t.Callable[..., t.Any])


def pass_config(f: F) -> F:
    def new_func(*args, **kwargs):  # type: ignore
        return f(click.get_current_context().obj, *args, **kwargs)

    return update_wrapper(t.cast(F, new_func), f)


option = click.option
command = click.command
argument = click.argument
group = click.group
Command = click.Command
Group = click.Group


def dict_print(d: dict[str, t.Any], indent=0, capitalize: t.Union[bool, int] = False):
    for k, v in d.items():
        if capitalize is True or capitalize > 0:
            k = '-'.join('ID' if word.lower() == 'id' else word.capitalize() for word in k.split('-'))

        if isinstance(v, dict):
            print('  ' * indent + k + ':')
            dict_print(v, indent=indent + 1, capitalize=capitalize if isinstance(capitalize, bool) else capitalize - 1)
        else:
            print('  ' * indent + k + ': ' + message_important(v))
