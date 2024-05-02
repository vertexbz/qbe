from __future__ import annotations

import os

import jinja2


def _setup_env(j2env: jinja2.Environment):
    j2env.filters['dirname'] = lambda s: os.path.dirname(s)
    j2env.filters['join_path'] = lambda p1, p2: os.path.join(p1, p2)
    j2env.filters['relative_to'] = lambda to, frm: os.path.relpath(to, os.path.dirname(frm))
    return j2env


_j2env = _setup_env(jinja2.Environment('{%', '%}', '{{', '}}', keep_trailing_newline=True))
_j2fsEnv = _setup_env(
    jinja2.Environment(
        '{%', '%}',
        '{{', '}}',
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
)


def template(template_string: str) -> jinja2.Template:
    return _j2env.from_string(template_string)


def render(template_string: str, context: dict = None) -> str:
    return template(template_string).render(context or {})
