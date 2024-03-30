class BedMeshOrigin:
    def __init__(self, config):
        printer = config.get_printer()  # type: Printer
        self.bed_mesh = printer.load_object(config, 'bed_mesh')  # type: BedMesh

    def get_status(self, *_):
        origin = self.bed_mesh.bmc.origin
        return {
            "tuple": origin,
            "text": origin[0] + "," + origin[1]
        }


def load_config(config):
    return BedMeshOrigin(config)
