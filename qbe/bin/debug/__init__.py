from __future__ import annotations

import importlib
from inspect import getmembers
import pkgutil

import qbe.cli as cli


@cli.group()
def debug():
    pass


__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.iter_modules(path=__path__, prefix=__name__ + '.'):
    im = importlib.import_module(module)
    for _, command in getmembers(im, lambda x: isinstance(x, (cli.Command, cli.Group))):
        debug.add_command(command)
