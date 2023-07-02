import os
import tempfile
from typing import Union
from .service import find, KlipperService, MoonrakerService, KlipperScreenService, SystemdService
from .runner import Pip, Command, Sudo, Apt, Shell, Systemctl
from ..utils.file import writefile


class filler:
    def __getattribute__(self, item):
        return None


class ServicesWrapper:

    @property
    def klipper(self) -> Union[KlipperService, None]:
        return find('klipper', cls=KlipperService) or filler()

    @property
    def moonraker(self) -> Union[MoonrakerService, None]:
        return find('moonraker', cls=MoonrakerService) or filler()

    @property
    def KlipperScreen(self) -> Union[KlipperScreenService, None]:
        return find('KlipperScreen', cls=KlipperScreenService) or filler()


services = ServicesWrapper()

apt = Apt()

_sudo_cp = Sudo('/bin/cp')
_sudo_mkdir = Sudo('/bin/mkdir')
_sudo_ln = Sudo('/bin/ln')
_sudo_rm = Sudo('/bin/rm')

systemctl = Systemctl()


def sudo_mkdir(path: str, recursive: bool = False):
    args = [path]
    if recursive:
        args.insert(0, '-p')
    return _sudo_mkdir.quiet(args).returncode == 0


def sudo_rm(path: str, recursive: bool = False, force=False):
    args = [path]
    if force:
        args.insert(0, '-f')
    if recursive:
        args.insert(0, '-r')
    return _sudo_rm.quiet(args).returncode == 0


def sudo_ln(source: str, target: str, symbolic: bool = False, force=False):
    args = [source, target]
    if force:
        args.insert(0, '-f')
    if symbolic:
        args.insert(0, '-s')
    return _sudo_ln.quiet(args).returncode == 0


def sudo_cp(source: str, target: str, recursive: bool = False):
    args = [source, target]
    if recursive:
        args.insert(0, '-r')
    return _sudo_cp.quiet(args).returncode == 0


def sudo_write(data: str, target: str):
    tmp = tempfile.NamedTemporaryFile()
    writefile(tmp.name, data)

    os.chmod(tmp.name, 0o644)
    success = sudo_cp(tmp.name, target)

    return success


__all__ = [
    'services', 'Command', 'Sudo', 'Pip', 'apt', 'Shell', 'sudo_cp', 'sudo_write', 'systemctl', 'find',
    'KlipperService', 'MoonrakerService', 'KlipperScreenService'
]
