import os
import jinja2

__all__ = ['render']

j2env = jinja2.Environment('{%', '%}', '{{', '}}', keep_trailing_newline=True)
j2env.filters['dirname'] = lambda s: os.path.dirname(s)
j2env.filters['join_path'] = lambda p1, p2: os.path.join(p1, p2)
j2env.filters['relative_to'] = lambda to, frm: os.path.relpath(to, os.path.dirname(frm))


def render(template: str, context: dict = {}):
    return j2env.from_string(template).render(context)
