from __future__ import annotations
from typing import TYPE_CHECKING, Type, Literal
from types import MethodType
from math import inf, sqrt
from extras.bed_mesh import BedMeshCalibrate, ZrefMode

if TYPE_CHECKING:
    from klippy import Printer
    from configfile import error as ConfigError
    from extras.bed_mesh import BedMesh


class DynamicBedMeshReference:
    def __init__(self, bed_mesh: BedMesh):
        self.bed_mesh = bed_mesh

    def get_status(self, *_):
        origin = self.bed_mesh.bmc.zero_ref_pos

        return {
            "tuple": origin,
            "text": 'None' if not origin else str(origin[0]) + "," + str(origin[1])
        }


def center_between(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] + b[0])/2, (a[1] + b[1])/2


def closest_to(points: list[tuple[float, float]], center: tuple[float, float]) -> tuple[float, float]:
    centermost = None
    min_distance = inf
    for point in points:
        distance = sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)

        if distance < min_distance:
            centermost = point
            min_distance = distance

    return centermost


def hooked_generate_points(
        self: BedMeshCalibrate,
        error: Type[ConfigError],
        probe_method: Literal['automatic', 'manual'] = 'automatic'
):
    # Run original method without ref point
    zero_ref_pos = self.zero_ref_pos
    self.zero_ref_pos = None
    BedMeshCalibrate._generate_points(self, error, probe_method)
    self.zero_ref_pos = zero_ref_pos

    # Calculate center of mesh
    center = center_between(self.mesh_min, self.mesh_max)
    # Update mesh config
    self.zero_ref_pos = closest_to(self.points, center)
    self.zero_reference_mode = ZrefMode.IN_MESH


def load_config(config):
    printer: Printer = config.get_printer()
    bed_mesh: BedMesh = printer.load_object(config, 'bed_mesh')

    bed_mesh.bmc._generate_points = MethodType(hooked_generate_points, bed_mesh.bmc)

    return DynamicBedMeshReference(bed_mesh)
