from __future__ import annotations

from typing import Any

import yaml
import yaml.loader


class PkgTag(yaml.YAMLObject):
    yaml_tag = u'!PKG'

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'Package\'s {repr(self.path)}'

    def __str__(self):
        return str(self.path)

    @classmethod
    def from_yaml(cls, _, node):
        return PkgTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.path)


class VarTag(yaml.YAMLObject):
    yaml_tag = u'!VAR'

    def __init__(self, variable):
        self.variable = variable

    def __repr__(self):
        return f'Variable {repr(self.variable)}'

    def __str__(self):
        return str(self.variable)

    def in_dict(self, dictionary):
        keys = self.variable.split(".")
        for key in keys:
            if isinstance(dictionary, dict) and key in dictionary:
                dictionary = dictionary[key]
            elif (value := getattr(dictionary, key, None)) is not None:
                dictionary = value
            else:
                return None
        return dictionary

    @classmethod
    def from_yaml(cls, _, node):
        return VarTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.variable)


class Loader(yaml.loader.Reader, yaml.loader.Scanner, yaml.loader.Parser, yaml.loader.Composer,
             yaml.loader.FullConstructor, yaml.loader.Resolver):
    def __init__(self, stream):
        yaml.loader.Reader.__init__(self, stream)
        yaml.loader.Scanner.__init__(self)
        yaml.loader.Parser.__init__(self)
        yaml.loader.Composer.__init__(self)
        yaml.loader.FullConstructor.__init__(self)
        yaml.loader.Resolver.__init__(self)


Loader.add_constructor(PkgTag.yaml_tag, PkgTag.from_yaml)
Loader.add_constructor(VarTag.yaml_tag, VarTag.from_yaml)


def load(stream) -> Any:
    return yaml.load(stream, Loader=Loader)


def dump(data, stream, **kw):
    return yaml.dump(data, stream, line_break='\n', sort_keys=True, **kw)


__all__ = ['load', 'dump', 'PkgTag', 'VarTag']
