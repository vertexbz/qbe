from __future__ import annotations

import logging
import os
from types import MethodType
from typing import TYPE_CHECKING, Type
import urllib.parse

from .file_manager import ExtendedFileManager
from ....application import FileRequestHandler

if TYPE_CHECKING:
    from components.file_manager.file_manager import FileManager
    from confighelper import ConfigHelper
    from server import Server


def register_static_file_handler(
    self: Server, pattern: str, file_path: str, force: bool = False,
    handler: Type[FileRequestHandler] = FileRequestHandler
) -> None:
    pattern = urllib.parse.quote(pattern, safe='/:')

    if pattern[0] != "/":
        pattern = "/server/files/" + pattern

    if os.path.isfile(file_path) or force:
        pattern += '()'
    elif os.path.isdir(file_path):
        if pattern[-1] != "/":
            pattern += "/"
        pattern += "(.*)"
    else:
        logging.info(f"Invalid file path: {file_path}")
        return

    logging.debug(f"Registering static file: ({pattern}) {file_path}")

    self.moonraker_app.mutable_router.add_handler(
        f"{self.moonraker_app._route_prefix}{pattern}", handler, {'path': file_path}
    )


def hook(config: ConfigHelper) -> None:
    server: Server = config.get_server()
    server.register_static_file_handler = MethodType(register_static_file_handler, server)

    file_manager: FileManager = server.load_component(config, 'file_manager')
    ExtendedFileManager.cast(file_manager)


__all__ = ['hook']
