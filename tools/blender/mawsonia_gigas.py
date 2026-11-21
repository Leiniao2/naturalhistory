"""
Procedural Mawsonia gigas (Early Cretaceous coelacanth, Brazil and North Africa).

A giant coelacanth about 4 metres long: a deep, heavy body covered in thick, rough, bony
scales, a big, broad head with a wide mouth and large eyes, paired lobed fins (fleshy,
scaly stalks fringed with rays) carried like limbs, a lobed second dorsal and anal fin,
a spiny first dorsal fin and the coelacanth's three-lobed tail with a small middle tuft.
Dark blue-grey with irregular pale spots like the living coelacanth (colours conjectural).
Swim style: faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/mawsonia_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mawsonia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.13, 0.17, 0.24)
FLANK = (0.22, 0.27, 0.36)
BELLY = (0.42, 0.46, 0.52)
SPOT = (0.82, 0.84, 0.82)
FIN = (0.18, 0.22, 0.30)
LOBE = (0.24, 0.29, 0.38)


def paint_extra(co, n, c):
    m = noise.noise(Vector(co) * 22.0)
    return nh.lerp(c, SPOT, 0.8 * nh.smoothstep(0.32, 0.42, m) * nh.smoothstep(-0.5, 0.0, n.z))


def lobe_fin(mb, s, root, d, length, chord, color):
    """A fleshy scaly stalk with a fan of fin rays at its end (a coelacanth lobe fin)."""
    root, d = Vector(root), Vector(d).normalized()
    mid = root + d * length * 0.5
    mb.add(nh.tube([root, mid, root + d * length * 0.62], [chord * 0.45, chord * 0.38, chord * 0.2], sides=8), LOBE)
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    lead = [mid - side * chord * 0.5, root + d * length * 1.2]
    trail = [mid + side * chord * 0.6 + Vector((0, chord * 0.4, 0)), root + d * length * 1.15 + Vector((0, chord * 0.6, 0))]
    mb.add(cc.membrane(cc.polyline(lead, 8), cc.polyline(trail, 8), nv=4, thickness=0.01,
                       normal_hint=d.cross(side)), color)


def make():
    axis = [(0.80, 0.0, 0.0, 0.0), (0.74, 0.0, 0.02, 0.035), (0.60, 0.0, 0.05, 0.08),
            (0.35, 0.0, 0.10, 0.17), (0.05, 0.0, 0.13, 0.22), (-0.25, 0.0, 0.13, 0.21),
            (-0.45, -0.005, 0.12, 0.17), (-0.62, -0.02, 0.10, 0.12), (-0.72, -0.03, 0.07, 0.07),
            (-0.77, -0.035, 0.0, 0.0)]
    jaw = [(-0.45, -0.13, 0.10, 0.03), (-0.62, -0.10, 0.08, 0.025), (-0.74, -0.07, 0.04, 0.018),
           (-0.78, -0.06, 0.0, 0.0)]
    s = tp.Spec(name="Mawsonia", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=paint_extra, mottle=0.1),
                power=2.0, jaw=jaw, hinge=(-0.45, -0.10), jaw_open=8, pivot="centre",
                eye=(0.09, -0.60, 0.04, 0.03), eye_col=(0.45, 0.55, 0.45), voxel=0.01, max_tris=11000,
                disp=cc.scales_disp(0.004, 22.0))

    def crisp(mb, s):
        # three-lobed tail: upper and lower lobes plus the small middle tuft
        mr.fin(mb, [(0, 0.55, 0.07), (0, 0.76, 0.03)], [(0, 0.68, 0.30), (0, 0.84, 0.05)], FIN)
        mr.fin(mb, [(0, 0.55, -0.07), (0, 0.76, -0.03)], [(0, 0.68, -0.30), (0, 0.84, -0.05)], FIN)
        mr.fin(mb, [(0, 0.80, 0.02), (0, 0.80, -0.02)], [(0, 0.92, 0.05), (0, 0.92, -0.05)], FIN)
        # spiny first dorsal
        mr.fin(mb, [(0, -0.10, 0.21), (0, 0.06, 0.21)], [(0, -0.06, 0.38), (0, 0.10, 0.24)], FIN)
        # lobed second dorsal and anal fins
        lobe_fin(mb, s, (0, 0.32, 0.15), (0, 0.6, 1.0), 0.16, 0.10, FIN)
        lobe_fin(mb, s, (0, 0.32, -0.15), (0, 0.6, -1.0), 0.16, 0.10, FIN)
        for sx in (1, -1):
            lobe_fin(mb, s, (sx * 0.10, -0.32, -0.10), (sx * 0.8, 0.5, -0.5), 0.20, 0.10, FIN)   # pectoral
            lobe_fin(mb, s, (sx * 0.08, 0.10, -0.18), (sx * 0.5, 0.6, -0.8), 0.15, 0.09, FIN)    # pelvic
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Mawsonia")
