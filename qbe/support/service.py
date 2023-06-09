import os
import argparse
import optparse  # pylint: disable=deprecated-module
from typing import Union, Type
from pystemd.systemd1 import Unit  # pylint: disable=import-error

from qbe.utils.obj import qrepr

argparse.ArgumentParser()


class SystemdService:
    def __init__(self, unit, service) -> None:
        self.id = unit.Id
        self.description = unit.Description
        self.srcdir = service.WorkingDirectory.decode('utf-8')
        self.envdir = os.path.dirname(os.path.dirname(service.ExecStart[0][0]))

        args = service.ExecStart[0][1][2:]
        args = [arg.decode('utf-8') for arg in args]
        self._load_cmd_args(args)

    def _load_cmd_args(self, exec_args: list[str]) -> None:
        pass

    __repr__ = qrepr()


class KlipperService(SystemdService):
    DEFAULT_TTY = '/tmp/printer'
    DEFAULT_SOCK = '/tmp/printer.sock'

    def _load_cmd_args(self, exec_args: list[str]) -> None:
        opts = optparse.OptionParser()
        opts.add_option('-I', '--input-tty', dest='inputtty', default=self.DEFAULT_TTY)
        opts.add_option('-a', '--api-server', dest='apiserver')
        opts.add_option('-l', '--logfile', dest='logfile')
        options, args = opts.parse_args(args=exec_args)

        self.configfile = os.path.expanduser(args[0])
        self.tty = os.path.expanduser(options.inputtty)
        self.apiserver = os.path.expanduser(options.apiserver)
        self.logfile = os.path.expanduser(options.logfile)

    def gcode(self, gcode: str):
        if not os.path.exists(self.tty):
            raise FileExistsError('klipper tty not exists')

        tty = os.open(self.tty, os.O_RDWR)
        os.write(tty, (gcode + '\n').encode('utf-8'))


class KlipperScreenService(SystemdService):
    def _load_cmd_args(self, exec_args: list[str]) -> None:
        parser = argparse.ArgumentParser()
        homedir = os.path.expanduser('~')

        parser.add_argument('-c', '--configfile', default=os.path.join(homedir, 'KlipperScreen.conf'))
        logdir = os.path.join(homedir, 'printer_data', 'logs')
        if not os.path.exists(logdir):
            logdir = '/tmp'

        parser.add_argument('-l', '--logfile', default=os.path.join(logdir, 'KlipperScreen.log'))
        options = parser.parse_args(args=exec_args)

        self.configfile = os.path.expanduser(options.configfile)
        self.logfile = os.path.expanduser(options.logfile)


class MoonrakerService(SystemdService):
    DEFAULT_DATA = os.path.expanduser('~/printer_data')

    def _load_cmd_args(self, exec_args: list[str]) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--datapath', default=self.DEFAULT_DATA)
        parser.add_argument('-c', '--configfile', default=None)
        parser.add_argument('-l', '--logfile', default=None)
        parser.add_argument('-n', '--nologfile', action='store_true', default=False)
        options = parser.parse_args(args=exec_args)

        self.datapath = os.path.expanduser(options.datapath)

        if options.configfile is not None:
            self.configfile = os.path.expanduser(options.configfile)
        else:
            self.configfile = os.path.join(self.datapath, 'config', 'moonraker.conf')

        if options.nologfile:
            self.logfile = None
        elif options.logfile:
            self.logfile = os.path.normpath(os.path.expanduser(options.logfile))
        else:
            self.logfile = os.path.join(self.datapath, 'logs', 'moonraker.log')


def find(*names: str, cls=SystemdService, throw=False) -> Union[Type[SystemdService], None]:
    try:
        for name in names:
            unit = Unit(name + '.service')
            unit.load()

            if unit.Unit.LoadState == b'loaded':
                return cls(unit.Unit, unit.Service)
    except:
        pass

    if throw:
        raise ValueError('Unknown service ' + names[0])
    return None
