from __future__ import annotations
import os
from abc import abstractmethod
from typing import Any, TypeVar, Generic, Union, TYPE_CHECKING
from qbe.utils.obj import qrepr
from qbe.utils.options import OptionsAwareOperation
from qbe.utils.yaml import LinkTag
from qbe.utils.yaml import PkgTag
from qbe.utils.context import build_context
import qbe.cli as cli

if TYPE_CHECKING:
    from qbe.config import Config
    from qbe.package import Section, Package
    from qbe.package_provider import Dependency

BP_C = TypeVar('BP_C', bound='Any')


class TargetPath:
    def __init__(self, main: str, link: Union[str, None] = None, default: Union[str, None] = None):
        self.main = main
        self.link = link
        self.default = default


class BaseProvider(Generic[BP_C]):
    def __init__(self, config: Config, package: Package, dependency: Dependency) -> None:
        super().__init__()
        self.config = config
        self.package = package
        self.dependency = dependency

    @classmethod
    @abstractmethod
    # pylint: disable-next=unused-argument
    def validate_config(cls, config: Any) -> BP_C:
        raise NotImplementedError()

    @abstractmethod
    # pylint: disable-next=unused-argument
    def process(self, config: BP_C, line: cli.Line, section: Section) -> None:
        raise NotImplementedError()

    def _context(self):
        return build_context(self.config, self.package, self.dependency)

    def _base_path(self, file: Union[PkgTag, str]):
        return self.dependency.qbe_definition if isinstance(file, PkgTag) else self.package.dir

    def _src_path(self, file: Union[PkgTag, str]):
        return os.path.join(self._base_path(file), str(file))

    def _resolve_target_dir(self, target: Union[str, TargetPath], subpath: str):
        if isinstance(target, str):
            return target

        if isinstance(target, TargetPath):
            return target.link if isinstance(subpath, LinkTag) else target.main

        raise ValueError('Invalid target provided')


class ConfigOperation(OptionsAwareOperation):
    def __init__(self, args) -> None:
        super().__init__()

        if isinstance(args, dict) and 'source' in args and 'target' in args:
            self.source: str = args['source']
            self.target: str = args['target']

            self.only = args.get('only', {})
            self.unless = args.get('unless', {})

        elif isinstance(args, str):
            self.source = args
            self.target = args

        elif isinstance(args, PkgTag):
            self.source = args
            self.target = args.path

        elif isinstance(args, list) and len(args) == 2 \
            and isinstance(args[0], (str, PkgTag)) \
            and isinstance(args[1], (str, LinkTag)):
            self.source = args[0]
            self.target = args[1]

        else:
            raise ValueError(f'Invalid config entry {args}')

    __repr__ = qrepr()
