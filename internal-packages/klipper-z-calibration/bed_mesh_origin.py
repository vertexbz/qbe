from . import bed_mesh


class BedMeshOrigin:
    def __init__(self, config):
        self.bed_mesh = config.get_printer().lookup_object('bed_mesh')  # type: bed_mesh.BedMeshCalibrate

    def get_status(self, *_):
        origin = self.bed_mesh.origin
        return {
            "tuple": origin,
            "text": origin[0] + "," + origin[1]
        }


def load_config(config):
    return BedMeshOrigin(config)
