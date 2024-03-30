class BedMeshOrigin:
    def __init__(self, config):
        self.printer = config.get_printer()  # type: Printer

    def get_status(self, *_):
        bed_mesh = self.printer.lookup_object(config, 'bed_mesh')  # type: BedMesh
        origin = bed_mesh.bmc.origin
        if not origin:
            origin = (175, 175)
        return {
            "tuple": origin,
            "text": origin[0] + "," + origin[1]
        }


def load_config(config):
    return BedMeshOrigin(config)
