import os
from qbe.utils import jinja
from .base import BaseStrategy, Skipped
from . import operation


@operation('template')
class TemplateConfigCommand(BaseStrategy):
    def execute(self, source: str, target: str) -> str:
        if os.path.exists(target):
            raise Skipped('%(target)s already exists')

        content = open(source, 'r', encoding='utf-8').read()
        content = jinja.render(content, self.provider._context())

        os.makedirs(os.path.dirname(target), exist_ok=True)
        
        output = open(target, "w", encoding='utf-8')
        output.write(content)
        output.close()

        return 'created %(target)s from template'
