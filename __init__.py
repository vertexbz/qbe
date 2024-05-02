from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING


def in_moonraker() -> bool:
    try:
        find_spec('moonraker.server')
    except:
        return False
    else:
        return True


if in_moonraker():
    from .moonraker import load
    if TYPE_CHECKING:
        from confighelper import ConfigHelper

    def load_component(config: ConfigHelper):
        return load(config)
