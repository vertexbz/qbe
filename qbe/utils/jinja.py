import os
import jinja2

__all__ = ['render']


def _setup_env(j2env: jinja2.Environment):
    j2env.filters['dirname'] = lambda s: os.path.dirname(s)
    j2env.filters['join_path'] = lambda p1, p2: os.path.join(p1, p2)
    j2env.filters['relative_to'] = lambda to, frm: os.path.relpath(to, os.path.dirname(frm))
    return j2env


j2env = _setup_env(jinja2.Environment('{%', '%}', '{{', '}}', keep_trailing_newline=True))
j2fsEnv = _setup_env(
    jinja2.Environment(
        '{%', '%}',
        '{{', '}}',
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
)


def render(template: str, context: dict = {}):
    return j2env.from_string(template).render(context)


def render_file(template_path: str, context: dict = {}) -> str:
    return j2fsEnv.get_template(template_path).render(context)
