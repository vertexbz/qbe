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

class Loader(yaml.loader.Reader, yaml.loader.Scanner, yaml.loader.Parser, yaml.loader.Composer, yaml.loader.FullConstructor, yaml.loader.Resolver):
    def __init__(self, stream):
        yaml.loader.Reader.__init__(self, stream)
        yaml.loader.Scanner.__init__(self)
        yaml.loader.Parser.__init__(self)
        yaml.loader.Composer.__init__(self)
        yaml.loader.FullConstructor.__init__(self)
        yaml.loader.Resolver.__init__(self)

Loader.add_constructor(PkgTag.yaml_tag, PkgTag.from_yaml)

__all__ = ['Loader', 'PkgTag']
