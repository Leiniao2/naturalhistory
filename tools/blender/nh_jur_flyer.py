"""
Parametric spread-winged flier/glider for the Jurassic batch (rhamphorhynchus_muensteri.py,
dimorphodon_macronyx.py, yi_qi.py, anchiornis_huxleyi.py, volaticotherium_antiquum.py).

The whole body (tail tip -> body -> neck -> head) is one Spine loft from control rings,
fused with the arm bones running along the wing's leading edge and the trailing legs.
Wings are thin panels (membranes or feather sheets) from a half-outline in the XY plane,
mirrored to both sides. Faces -Y, span along X, pivot at the body centre (Soar style).
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from mathutils import Vector

import nh_model as nh
import nh_jur_kit as kit


@dataclass
class Spec:
    name: str
    rows: list                         # spine rings (x, y, z, half width, half height), tail tip -> snout
    paint: Callable                    # body colour fn
    wing: list                         # half outline [(x, y), ...] for the right wing (x > 0), closed
    wing_color: Callable               # fn(co, n) for the wings
    wing_z: float = 0.0
    wing_thick: float = 0.006
    dihedral: float = 0.08             # wing tips raised by this fraction of x
    arm: list = field(default_factory=list)   # leading-edge bone points (right side) [(x, y, z)]
    arm_r: list = field(default_factory=list)
    legs: list = field(default_factory=list)  # right leg points [(x, y, z)], mirrored
    leg_r: list = field(default_factory=list)
    hind_wing: Optional[list] = None   # optional second wing outline (Anchiornis' leg feathers)
    eye: tuple = (0.03, -0.3, 0.05)    # right eye centre
    eye_r: float = 0.012
    eye_color: tuple = kit.EYE
    voxel: float = 0.006
    max_tris: int = 7000
    extras: Optional[Callable] = None  # extras(spine) -> (fused [(bm, col)], crisp [(bm, col)])
    feather_lines: int = 0             # number of separated feather tips cut into each wing's trailing edge


def wing_panel(outline, sx, z, thick, dihedral):
    pts = [(sx * x, y, z + abs(x) * dihedral) for x, y in outline]
    if sx < 0:
        pts = list(reversed(pts))
    bm = nh.flat_panel(pts, thickness=thick)
    # subdivide so vertex-colour markings on the wings have vertices to land on
    import bmesh
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    return bm


def build(sp):
    spine = kit.Spine(sp.rows, steps=4)
    fused = [(spine.mesh(sides=16), (0.5,) * 3)]
    crisp = []
    for sx in (1, -1):
        if sp.arm:
            pts = [(sx * x, y, z + abs(x) * sp.dihedral) for x, y, z in sp.arm]
            fused.append((kit.limb(pts, sp.arm_r, sides=8), (0.5,) * 3))
        if sp.legs:
            pts = [(sx * x, y, z + abs(x) * sp.dihedral) for x, y, z in sp.legs]
            fused.append((kit.limb(pts, sp.leg_r, sides=8), (0.5,) * 3))
    if sp.extras:
        ef, ec = sp.extras(spine)
        fused += ef
        crisp += ec
    body = kit.fuse_parts(fused, sp.voxel, sp.max_tris, smooth=4)
    mb = nh.MeshBuilder()
    mb.add(body, sp.paint)
    for sx in (1, -1):
        mb.add(wing_panel(sp.wing, sx, sp.wing_z, sp.wing_thick, sp.dihedral), sp.wing_color, smooth=False)
        if sp.hind_wing:
            mb.add(wing_panel(sp.hind_wing, sx, sp.wing_z - 0.004, sp.wing_thick, sp.dihedral), sp.wing_color, smooth=False)
    kit.eyes(mb, sp.eye, sp.eye_r, iris=sp.eye_color)
    for bm, col in crisp:
        mb.add(bm, col, smooth=False)
    return kit.finish(mb, sp.name, pivot="center")


PREVIEW = dict(background=(0.45, 0.58, 0.70), views=((35, 25), (0, 89), (-90, 5)))
