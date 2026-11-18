"""
Procedural Thalattoarchon saurophagis (Middle Triassic macropredatory ichthyosaur, ~8.6 m)
for the map (Swim style).

The "lizard-eating sea ruler" from the Fossil Hill Member of Nevada, about 244 million
years ago, the first ocean predator able to take prey as large as itself. A robust,
fairly long-bodied early ichthyosaur with a big, deep skull, a shorter, stouter snout than
most ichthyosaurs, and big, blade-like cutting teeth with sharp front and back edges for
slicing other marine reptiles; moderate flippers, a low dorsal fin and an early,
only weakly crescent-shaped tail fluke. Built with the shared ichthyosaur recipe
(nh_ichthyosaur.py) plus a row of crisp blade teeth along the jaws. Countershaded slate
grey with darker mottling (speculative). Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/thalattoarchon_saurophagis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Thalattoarchon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

TOOTH = (0.94, 0.91, 0.82)

SPEC = ich.IchthyosaurSpec(
    name="Thalattoarchon",
    voxel=0.012, max_tris=16000,
    snout_len=0.22, snout_r=0.046, snout_tip_r=0.014,
    eye_r=0.036, head_h=0.090, head_w=0.078,
    body_h=0.125, belly_k=1.08, body_w=0.110, y_max=-0.30, rear_k=0.75,
    y_ped=0.74, ped_h=0.026, ped_w=0.018,
    tail_bend=10.0, y_bend=0.64,
    fore=(-0.45, 0.20, 0.09), fore_shape=0.30, fore_droop=32.0, fore_sweep=42.0,
    hind=(0.02, 0.14, 0.065), hind_shape=0.25, hind_droop=36.0, hind_sweep=46.0,
    dorsal=(-0.02, 0.07, 0.26), dorsal_rake=0.5,
    fluke_up=0.09, fluke_down=0.17, fluke_sweep=0.17, fluke_chord=0.10, fluke_lunate=0.03,
    back=(0.15, 0.17, 0.20), flank=(0.38, 0.40, 0.43), belly=(0.88, 0.86, 0.80),
    fin=(0.11, 0.12, 0.15), mottle=(0.22, 0.24, 0.28), mottle_k=0.45,
    shade_line=-0.20, ring=(0.72, 0.66, 0.52), ring_plates=13,
)


def teeth(mb, body, shape):
    surf = tt.Surface(body)
    s = SPEC
    y0, y1 = -0.985, shape.y_eye - s.eye_r * 0.4
    n = 9
    for i in range(n):
        t = (i + 0.5) / n
        y = y0 + (y1 - y0) * t
        z = shape.zc(y) + shape.mouth_z(y) * shape.hb(y)
        ln = 0.046 * (0.75 + 0.35 * math.sin(math.pi * min(1.0, t * 1.4)))
        r = 0.0115
        for sx in (1, -1):
            loc, nrm = surf.hit((sx * 2.0, y, z), (-sx, 0, 0))
            if loc is None:
                continue
            base = loc - nrm * r * 0.8 + Vector((0, 0, 0.004))
            # flat, slightly recurved blade
            blade = nh.tube([base, base + Vector((0, 0.08 * ln, -0.6 * ln)), base + Vector((0, 0.22 * ln, -ln))],
                            [r, r * 0.6, 0.0], sides=6, scale_xy=None)
            mb.add(blade, TOOTH, smooth=False)
            if i % 2 == 0:
                b2 = loc - nrm * r * 0.8 + Vector((0, 0.012, -0.010))
                mb.add(tt.cone(b2, b2 + Vector((0, -0.05 * ln, 0.8 * ln)), r * 0.85), TOOTH, smooth=False)


def build():
    shape = ich.Ichthyosaur(SPEC)
    grey = (0.5, 0.5, 0.5)
    parts = nh.MeshBuilder()
    parts.add(ich.loft(-1.0, SPEC.y_ped + 0.02, 140, 40, shape.section), grey)
    for sg in (-1, 1):
        parts.add(shape.flipper(sg, SPEC.fore, SPEC.fore_shape, SPEC.fore_droop, SPEC.fore_sweep), grey)
        parts.add(shape.flipper(sg, SPEC.hind, SPEC.hind_shape, SPEC.hind_droop, SPEC.hind_sweep), grey)
        parts.add(shape.orbit(sg), grey)
    parts.add(shape.dorsal(), grey)
    parts.add(shape.fluke(), grey)
    fused = parts.fuse(voxel=SPEC.voxel, smooth=6, smooth_factor=0.5, max_tris=SPEC.max_tris)
    shape.groove_mouth(fused)
    mb = nh.MeshBuilder()
    teeth(mb, fused, shape)
    mb.add(fused, shape.colour)
    for sg in (-1, 1):
        shape.eye(mb, sg)
        shape.nostril(mb, sg)
    obj = mb.to_object(SPEC.name, roughness=0.45)
    ich.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Thalattoarchon", background=(0.05, 0.18, 0.24), views=((35, 25), (-90, 4), (30, 62)))
