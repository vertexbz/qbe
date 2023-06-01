from __future__ import annotations
import os
import pprint
import time
import shlex
from itertools import chain
import qbe.cli as cli
from qbe.handler import NotificationBag
from qbe.handler import handler
from qbe.package_provider import UpdateResult, dependency_provider, build_dependency
from qbe.package_provider.internal import InternalDependency
from qbe.package import load as package_load, load_config as package_load_config, Result, Status, Section, Detail
from qbe.feature_provider import AVAILABLE_PROVIDERS
from qbe.config import Config
from qbe.trigger import multihandler


@cli.command(short_help='Display paths')
@cli.pass_config
def paths(config: Config):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config.paths.__dict__)
