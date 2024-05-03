from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from typing import Callable, Optional, Literal

from ..adapter.file import writefile


class CommandError(Exception):
    def __init__(self, message: str, command: str, cwd: str, env: dict, *args):
        super().__init__(message, *args)
        self.command = command
        self.env = env
        self.cwd = cwd


async def shell(
    command: str, cwd: Optional[str] = None, strip=False, env: Optional[dict] = None,
    raw_std=False,
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None
):
    computed_env = {var: os.environ[var] for var in ('HOME', 'SHELL', 'TERM') if var in os.environ}
    if env:
        computed_env.update(env)

    # Create subprocess with stdout and stderr set to PIPE
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=computed_env
    )

    # asyncio subprocess interaction based on https://docs.python.org/3/library/asyncio-subprocess.html
    stdout, stderr = [], []

    while not (proc.stdout.at_eof() and proc.stderr.at_eof()):
        # Create task for stdout and stderr
        tasks = [
            asyncio.create_task(proc.stdout.readline()),
            asyncio.create_task(proc.stderr.readline())
        ]

        # Wait for any to finish
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Check results of done tasks
        for fut in done:
            result = await fut
            result = result.decode('utf-8')

            if raw_std:
                lines = [result]
            else:
                lines = map(lambda s: s.rstrip(), result.replace('\r', '\n').splitlines())

            for line in lines:
                if not line:
                    continue

                if fut is tasks[0]:
                    stdout.append(line)
                    if stdout_callback:
                        stdout_callback(line)
                elif fut is tasks[1]:
                    stderr.append(line)
                    if stderr_callback:
                        stderr_callback(line)

        # Cancel pending tasks
        for fut in pending:
            fut.cancel()

    await proc.wait()

    if proc.returncode > 0:
        raise CommandError('\n'.join(stderr), command, cwd, env)

    response = '\n'.join(stdout)
    if strip and response:
        response = response.strip()

    return response


async def sudo(
    command: str, cwd: Optional[str] = None, strip=False, env: Optional[dict] = None,
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None
):
    return await shell(
        '/usr/bin/sudo ' + command,
        cwd=cwd, strip=strip, env=env, stdout_callback=stdout_callback, stderr_callback=stderr_callback
    )


async def sudo_mkdir(path: str, recursive: bool = False, stdout_callback: Optional[Callable[[str], None]] = None):
    args = ['mkdir -v', path]
    if recursive:
        args.insert(1, '-p')

    await sudo(' '.join(args), stdout_callback=stdout_callback)


async def sudo_rm(
    path: str, recursive: bool = False, force=False,
    stdout_callback: Optional[Callable[[str], None]] = None
):
    args = ['rm -v', path]
    if force:
        args.insert(1, '-f')
    if recursive:
        args.insert(1, '-r')

    await sudo(' '.join(args), stdout_callback=stdout_callback)


async def sudo_ln(
    source: str, target: str, symbolic: bool = False, force=False,
    stdout_callback: Optional[Callable[[str], None]] = None
):
    args = ['ln', source, target]
    if force:
        args.insert(1, '-f')
    if symbolic:
        args.insert(1, '-s')

    await sudo(' '.join(args), stdout_callback=stdout_callback)


async def sudo_cp(
    source: str, target: str, recursive: bool = False,
    stdout_callback: Optional[Callable[[str], None]] = None
):
    args = ['cp -v', source, target]
    if recursive:
        args.insert(1, '-r')

    await sudo(' '.join(args), stdout_callback=stdout_callback)


async def sudo_write(data: str, target: str, stdout_callback: Optional[Callable[[str], None]] = None):
    with tempfile.NamedTemporaryFile() as tmp:
        writefile(tmp.name, data)

        os.chmod(tmp.name, 0o644)

        await sudo_cp(tmp.name, target, stdout_callback=stdout_callback)


async def sudo_systemctl_daemon_reload():
    await sudo('systemctl daemon-reload')


async def sudo_systemctl_service(
    action: Literal['reload', 'restart', 'stop', 'start'], service: str,
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None
):
    await sudo(f'systemctl {action} {service}', stdout_callback=stdout_callback, stderr_callback=stderr_callback)


async def pip(
    command: str, venv: Optional[str] = None,
    cwd: Optional[str] = None, env: Optional[dict] = None, strip=False,
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None
):
    if env is None:
        env = {}
    else:
        env = {**env}

    executable = shutil.which('pip3') or shutil.which('pip3')
    if venv:
        env['VIRTUAL_ENV'] = venv
        env['PATH'] = os.path.join(venv, 'bin') + ':' + os.environ.get('PATH')
        executable = os.path.join(venv, 'bin', 'pip')

    return await shell(
        executable + ' ' + command, cwd=cwd,
        strip=strip, env=env, stdout_callback=stdout_callback, stderr_callback=stderr_callback
    )
