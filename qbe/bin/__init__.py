import pkgutil
import importlib
import os
from typing import Union
from inspect import getmembers
import click

from qbe.config import load, get_config_file_name, Config, DEFAULT_CONFIG_FILE_NAME

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


def _get_config_path(config_dir: str) -> Union[str, None]:
    config = get_config_file_name(config_dir)
    if config is not None:
        return os.path.join(config_dir, config)

    return None


def _get_default_config_path() -> str:
    config = _get_config_path(os.path.expanduser('~'))
    if config is not None:
        return config

    config = _get_config_path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    if config is not None:
        return config

    return os.path.join(os.path.expanduser('~'), DEFAULT_CONFIG_FILE_NAME)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--config', default=_get_default_config_path)
@click.pass_context
def entry(ctx: click.Context, config: str):
    ctx.obj = cfg = load(config) if os.path.isfile(config) else Config()

    @ctx.call_on_close
    def close_config():
        if cfg.is_dirty:
            print('now should save config back?')


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    im = importlib.import_module(module)
    for _, command in getmembers(im, lambda x: isinstance(x, click.Command)):
        entry.add_command(command)
