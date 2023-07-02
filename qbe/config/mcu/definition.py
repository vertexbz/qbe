from __future__ import annotations
from typing import Union
import os

from qbe.utils import jinja
from qbe.utils.file import readfile
from qbe.utils.path import qbedir
from qbe.utils.yaml import yaml_to_obj


class MCUConfigTemplate:
    def __init__(self, template_string):
        self.template = jinja.template(template_string)
        
    def render(self, options: dict):
        return self.template.render(options)

    @classmethod
    def from_file(cls, configpath: str):
        template_string = readfile(configpath)
        return cls(template_string)


class MCUConfig:
    def __init__(self, definition: MCUDefinition, firmware_config: str, bootloader: Union[None, str] = None,
                 bootloader_config: Union[None, str] = None):
        if bootloader is not None and bootloader_config is None:
            raise AssertionError('bootloader is set but bootloader_config is missing')
        if bootloader is None and bootloader_config is not None:
            raise AssertionError('bootloader type is unknown but bootloader_config is set')
        self.definition = definition
        self.firmware = MCUConfigTemplate.from_file(os.path.join(definition.basepath, firmware_config))
        self.bootloader_type = bootloader
        self.bootloader = MCUConfigTemplate.from_file(
            os.path.join(definition.basepath, bootloader_config)) if bootloader_config is not None else None

    @classmethod
    def from_config(cls, definition: MCUDefinition, config: Union[str, dict]):
        if isinstance(config, str):
            return cls(definition, config)

        firmware = config.pop('firmware')
        bootloader = config.pop('bootloader', None)
        if bootloader is None:
            return cls(definition, firmware)

        return cls(definition, firmware, bootloader.pop('type'), bootloader.pop('config'))


class MCUDefinition:
    def __init__(self, basepath: str, **kw):
        self.basepath = basepath
        self.name = kw.pop('name')

        self.modes: dict[str, MCUConfig] = {
            mode: MCUConfig.from_config(self, config) for mode, config in kw.pop('mode').items()
        }

        flash = kw.pop('flash', [])
        if isinstance(flash, str):
            flash = [flash]
        self.flash: list[str] = flash

    @property
    def default_mode(self):
        return next(iter(self.modes))

    @classmethod
    def from_preset_name(cls, preset: str) -> MCUDefinition:
        basepath = os.path.join(qbedir, 'mcus', preset)
        return yaml_to_obj(os.path.join(basepath, 'mcu.yml'), lambda **data: cls(basepath, **data))
