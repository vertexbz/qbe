from typing import Union
import click


def qrepr(val=lambda v: vars(v)):
    def __repr__(self) -> str:
        type_str = click.style(type(self).__name__, fg='blue', dim=True)
        id_str = click.style(hex(id(self)), dim=True)

        c_start = click.style('<', fg='yellow', dim=True)
        c_end = click.style('>', fg='yellow', dim=True)
        return f'{c_start}{type_str}:{id_str} {val(self)}{c_end}'

    return __repr__


def is_valid_attribute(obj, attr: str):
    return isinstance(getattr(type(obj), attr), property) and not attr.startswith('_')


def get_dict_attr(obj, attr):
    val = getattr(obj, attr)
    if hasattr(val, '__dict__'):
        return val.__dict__
    return val


def qdict():
    @property
    def __dict__(self):
        return {attr: get_dict_attr(self, attr) for attr in dir(type(self)) if is_valid_attribute(self, attr)}

    return __dict__


def obj_to_env(obj: Union[object, dict], prefix: str = 'QBE_') -> dict[str, str]:
    env = {}

    if not isinstance(obj, dict):
        obj = {attr: getattr(obj, attr) for attr in dir(type(obj)) if is_valid_attribute(obj, attr)}

    for k, v in obj.items():
        if v is None:
            continue

        if isinstance(v, dict):
            env.update(obj_to_env(v, prefix + k.upper() + '_'))
        elif not isinstance(v, (str, int, float, bool)):
            env.update(obj_to_env(v, prefix + k.upper() + '_'))
        else:
            env[prefix + k.upper()] = str(v)

    return env
