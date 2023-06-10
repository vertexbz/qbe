import io
import os
import requirements
from qbe.utils.err import OperationFailed
import subprocess


class Command:
    def __init__(self, command: str, **kw) -> None:
        self.command = command
        self.cwd = kw.pop('cwd', None)
        self.env = kw.pop('env', None)
        self.args = kw.pop('args', [])

    def _get_args(self, args: list[str]):
        return [self.command, *self.args, *args]

    def run(self, args: list[str], **kw) -> subprocess.CompletedProcess:
        throw = kw.pop('throw', True)
        try:
            env = kw.pop('env', None)
            if self.env is not None:
                tmp = {}
                tmp.update(self.env)
                if env is not None:
                    tmp.update(env)
                env = tmp

            rkw = {'cwd': self.cwd, 'env': env, **kw, 'check': True}
            return subprocess.run(self._get_args(args), **rkw)
        except subprocess.CalledProcessError as e:
            if throw:
                raise OperationFailed(e.stderr.decode('utf-8'))
            else:
                return e

    def quiet(self, args: list[str], **kw) -> subprocess.CompletedProcess:
        return self.run(args, **kw, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def piped(self, args: list[str], **kw) -> subprocess.CompletedProcess:
        return self.run(args, **kw, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def attached(self, args: list[str], **kw) -> subprocess.CompletedProcess:
        return self.run(args, **kw, stderr=subprocess.PIPE)

    def noerr(self, args: list[str], **kw) -> subprocess.CompletedProcess:
        return self.run(args, **kw, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


class Sudo(Command):
    def _get_args(self, args: list[str]) -> list[str]:
        return ['/usr/bin/sudo', *super()._get_args(args)]


class Shell(Command):
    def __init__(self, **kw) -> None:
        super().__init__('/bin/sh', **kw)


class Systemctl(Sudo):
    def __init__(self):
        super().__init__('/bin/systemctl')

    def daemon_reload(self, **kw):
        self.quiet(['daemon-reload'], throw=True, **kw)

    def reload(self, service: str, **kw):
        self.quiet(['reload', service], throw=True, **kw)

    def restart(self, service: str, **kw):
        self.quiet(['restart', service], throw=True, **kw)

    def stop(self, service: str, **kw):
        self.quiet(['stop', service], throw=True, **kw)

    def start(self, service: str, **kw):
        self.quiet(['start', service], throw=True, **kw)

    def enable(self, service: str, **kw):
        self.quiet(['enable', service], throw=True, **kw)

    def disable(self, service: str, **kw):
        self.quiet(['disable', service], throw=True, **kw)


class Apt():
    def __init__(self) -> None:
        self.apt = Sudo('/usr/bin/apt', args=[])
        self.dpkg = Command('/usr/bin/dpkg-query', args=['--show', '--showformat=${db:Status-Status}'])

    def _should_install(self, requirement: str):
        result = self.dpkg.noerr([requirement], throw=False)
        return result.returncode != 0 or b'installed' != result.stdout

    def install(self, requirement_list: list[str]) -> bool:
        requirements = [
            requirement
            for requirement in requirement_list
            if self._should_install(requirement)
        ]

        if len(requirements) > 0:
            self.apt.quiet(['install', '-y', *requirements])
            return True

        return False


class Pip(Command):
    def __init__(self, venv: str, **kw) -> None:
        super().__init__(os.path.join(venv, 'bin', 'pip'), **kw)
        self._packages = None
        self._env = {
            'VIRTUAL_ENV': venv,
            'PATH': os.path.join(venv, 'bin') + ':' + os.environ.get('PATH'),
        }

    def _installed_packages(self) -> set[str]:
        if self._packages is None:
            packages_str: bytes = self.piped(['freeze']).stdout
            reqs = requirements.parse(io.StringIO(packages_str.decode('utf-8')))
            self._packages = set([requirement.name.lower() for requirement in reqs])

        return self._packages

    def _should_install(self, requirement: str):
        return requirement.lower() not in self._installed_packages()

    def install(self, requirement_list: list[str]) -> bool:
        requirements = [
            requirement
            for requirement in requirement_list
            if self._should_install(requirement)
        ]

        if len(requirements) > 0:
            self.quiet(['install', *requirements], env=self._env)
            return True

        return False

    def _requirements_from_file(self, requirements_file: str):
        with open(requirements_file, 'r') as fd:
            reqs = requirements.parse(fd)
            return [requirement.name.lower() for requirement in reqs]

    def _should_install_requirements_from_file(self, requirements_file: str):
        installed = self._installed_packages()
        reqs = self._requirements_from_file(requirements_file)
        for req in reqs:
            if req not in installed:
                return True

        return False

    def install_requirements(self, requirements_file: str):
        if self._should_install_requirements_from_file(requirements_file):
            self.quiet(['install', '-r', requirements_file], env=self._env)
            return True

        return False
