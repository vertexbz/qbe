class BedMeshOrigin:
    def __init__(self, config):
        self.printer = config.get_printer()  # type: Printer

    def get_status(self, *_):
        bed_mesh = self.printer.lookup_object('bed_mesh')  # type: BedMesh
        origin = bed_mesh.bmc.origin
        return {
            "tuple": origin,
            "text": 'None' if not origin else str(origin[0]) + "," + str(origin[1])
        }


def load_config(config):
    return BedMeshOrigin(config)
