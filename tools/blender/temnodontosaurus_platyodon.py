"""
Procedural Temnodontosaurus platyodon (Early Jurassic ichthyosaur, England and Germany)
for the map (Swim style).

One of the largest Jurassic ichthyosaurs, up to about 9 m long and the top predator of
the early Jurassic seas: a long, fairly slender, dolphin-shaped body, a long, robust
snout lined with big conical teeth, huge eyes (the largest of any known animal relative
to the skull, each ringed by bony sclerotic plates), fore and hind flippers of similar
size, a triangular dorsal fin and a crescent tail fluke. Painted dark blue-grey above
with a faint flank band and a pale belly (countershading as in other ichthyosaurs).

Built with the shared ichthyosaur recipe (nh_ichthyosaur.py) plus crisp teeth along the
mouth line. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/temnodontosaurus_platyodon.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Temnodontosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402
from mathutils import Vector  # noqa: E402

TOOTH = (0.94, 0.91, 0.80)

SPEC = ich.IchthyosaurSpec(
    name="Temnodontosaurus",
    voxel=0.014, max_tris=20000,
    snout_len=0.36, snout_r=0.040, snout_tip_r=0.010,
    eye_r=0.062, head_h=0.095, head_w=0.078,
    body_h=0.150, belly_k=1.05, body_w=0.125, y_max=-0.22, rear_k=0.70,
    y_ped=0.64, ped_h=0.028, ped_w=0.018,
    tail_bend=20.0, y_bend=0.52,
    fore=(-0.42, 0.30, 0.10), fore_shape=0.30, fore_droop=30.0, fore_sweep=40.0,
    hind=(0.10, 0.24, 0.085), hind_shape=0.30, hind_droop=32.0, hind_sweep=42.0,
    dorsal=(0.02, 0.13, 0.26), dorsal_rake=0.6,
    fluke_up=0.30, fluke_down=0.32, fluke_sweep=0.28, fluke_chord=0.085, fluke_lunate=0.13,
    back=(0.11, 0.14, 0.20), flank=(0.32, 0.36, 0.42), belly=(0.86, 0.85, 0.80),
    fin=(0.09, 0.11, 0.15), mottle=(0.20, 0.23, 0.28), mottle_k=0.30, stripe=(0.12, 0.14, 0.18),
    shade_line=-0.18, ring=(0.80, 0.74, 0.58), ring_plates=14,
)


def build():
    sp = SPEC
    ic = ich.Ichthyosaur(sp)
    grey = (0.5, 0.5, 0.5)
    parts = nh.MeshBuilder()
    parts.add(ich.loft(-1.0, sp.y_ped + 0.02, 140, 40, ic.section), grey)
    for sg in (-1, 1):
        parts.add(ic.flipper(sg, sp.fore, sp.fore_shape, sp.fore_droop, sp.fore_sweep), grey)
        parts.add(ic.flipper(sg, sp.hind, sp.hind_shape, sp.hind_droop, sp.hind_sweep), grey)
        parts.add(ic.orbit(sg), grey)
    parts.add(ic.dorsal(), grey)
    parts.add(ic.fluke(), grey)
    fused = parts.fuse(voxel=sp.voxel, smooth=6, smooth_factor=0.5, max_tris=sp.max_tris)
    ic.groove_mouth(fused)
    mb = nh.MeshBuilder()
    mb.add(fused, ic.colour)
    for sg in (-1, 1):
        ic.eye(mb, sg)
        ic.nostril(mb, sg)
    # big conical teeth along the mouth line of the snout, upper row pointing down, lower up
    y0, y1 = -0.96, ic.y_eye - sp.eye_r * 1.2
    n = 16
    for i in range(n):
        y = y0 + (y1 - y0) * i / (n - 1)
        w = ic.w(y)
        z = ic.zc(y) + ic.mouth_z(y) * ic.hb(y)
        ln = 0.012 + 0.012 * (i / (n - 1))
        for sg in (-1, 1):
            b = Vector((sg * w * 0.92, y, z + 0.002))
            mb.add(nh.tube([b, b + Vector((sg * ln * 0.25, -ln * 0.15, -ln))], [ln * 0.3, 0.0], sides=5), TOOTH, smooth=False)
            if i % 2:
                b = Vector((sg * w * 0.9, y + 0.006, z - 0.002))
                mb.add(nh.tube([b, b + Vector((sg * ln * 0.25, -ln * 0.1, ln * 0.85))], [ln * 0.28, 0.0], sides=5), TOOTH, smooth=False)
    obj = mb.to_object(sp.name, roughness=0.45)
    ich.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Temnodontosaurus", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (30, 62)))
