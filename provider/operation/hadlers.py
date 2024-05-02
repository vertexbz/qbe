from __future__ import annotations

import errno
import os
import shutil

from ...adapter.command import sudo_ln, sudo_rm, sudo_mkdir, sudo_write
from ...adapter.file import readfile, writefile
from ...adapter.jinja import render


def link_handler(source: str, target: str, context: dict) -> bool:
    if os.path.islink(target) and os.readlink(target) == source:
        return False

    if os.path.exists(target):
        if os.path.islink(target):
            os.unlink(target)
        else:
            shutil.rmtree(target)
    else:
        os.makedirs(os.path.dirname(target), exist_ok=True)

    if os.path.islink(target):
        os.remove(target)

    os.symlink(source, target)
    return True


def blueprint_handler(source: str, target: str, context: dict) -> bool:
    if os.path.exists(target):
        return False

    os.makedirs(os.path.dirname(target), exist_ok=True)

    try:
        shutil.copytree(source, target)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(source, target)
        else:
            raise exc

    return True


def template_handler(source: str, target: str, context: dict) -> bool:
    if os.path.exists(target):
        return False

    content = readfile(source)
    content = render(content, context)

    os.makedirs(os.path.dirname(target), exist_ok=True)

    writefile(target, content)

    return True


async def system_template_handler(source: str, target: str, context: dict) -> bool:
    contents = readfile(source)
    contents = render(contents, context)

    if os.path.exists(target) and readfile(target) == contents:
        return False

    await sudo_mkdir(os.path.dirname(target), recursive=True)
    await sudo_write(contents, target)
    return True


async def system_blueprint_handler(source: str, target: str, context: dict) -> bool:
    if os.path.exists(target):
        return False

    contents = readfile(source)
    contents = render(contents, context)
    await sudo_mkdir(os.path.dirname(target), recursive=True)
    await sudo_write(contents, target)
    return True


async def system_link_handler(source: str, target: str, context: dict) -> bool:
    if os.path.islink(target) and os.readlink(target) == source:
        return False

    if os.path.exists(target):
        await sudo_rm(target, force=True)
    else:
        await sudo_mkdir(os.path.dirname(target), recursive=True)

    await sudo_ln(source, target, symbolic=True)
    return True

