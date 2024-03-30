from typing import TYPE_CHECKING
from configfile import error as ConfigError

if TYPE_CHECKING:
    from configfile import ConfigWrapper
    from extras.bed_mesh import BedMesh
    from klippy import Printer


def get_xy(config: ConfigWrapper, name: str, extension_name: str):
    value = config.get(name, None)
    if value is None:
        return None

    try:
        x_pos, y_pos = value.split(',')
        return float(x_pos), float(y_pos)
    except:
        raise ConfigError("Unable to parse %s coordinates in %s" % (name, extension_name,))


class BedMeshOrigin:
    def __init__(self, config: ConfigWrapper):
        self.printer: Printer = config.get_printer()
        self.default = get_xy(config, "default_xy", config.get_name())

    def get_status(self, *_):
        bed_mesh: BedMesh = self.printer.lookup_object('bed_mesh')
        origin = bed_mesh.bmc.origin

        if not origin:
            origin = self.default

        return {
            "tuple": origin,
            "text": 'None' if not origin else str(origin[0]) + "," + str(origin[1])
        }


def load_config(config):
    return BedMeshOrigin(config)
