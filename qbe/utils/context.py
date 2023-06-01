from __future__ import annotations
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from qbe.config import Config
    from qbe.package import Package
    from qbe.package_provider import Dependency

def build_context(config: Config, package: Package, dependency: Dependency):
    return {
        'user': config.user,
        'paths': config.paths,
        'dirs': {
            'venv': os.path.join(config.paths.venvs, package.name),
            'pkg': package.dir
        },
        'options': dependency.options
    }
