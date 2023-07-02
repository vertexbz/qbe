import os
from qbe.utils import jinja
from qbe.utils.file import readfile
from qbe.utils.file import writefile
from .base import BaseStrategy, Skipped
from . import operation


@operation('template')
class TemplateConfigCommand(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.exists(target):
            raise Skipped('%(target)s already exists')

        content = readfile(source)
        content = jinja.render(content, self.provider._context())

        os.makedirs(os.path.dirname(target), exist_ok=True)

        writefile(target, content)

        return 'created %(target)s from template'
