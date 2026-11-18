"""
Procedural Deiphon forbesi (mid-Silurian cheirurid trilobite of Bohemia and Britain, about
3 cm long) for map colonies (Swim style).

A bizarre, probably free-swimming trilobite: its head is little more than a huge,
balloon-like, tuberculate glabella with long, outward-curving genal spines; the narrow
thorax of nine segments has its pleurae drawn out into long, free spines; and the tiny
pygidium carries a pair of long, backward-sweeping spines. Light, spiny build for life
in open water. Pale amber with darker spines. Built with nh_sil_trilobite.py (+ the
glabella and pygidial spines via nh_sil_extra). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/deiphon_forbesi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DeiphonForbesi.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402
import nh_sil_extra as ex  # noqa: E402

SPEC = tr.Spec(
    name="DeiphonForbesi",
    length=1.2, segments=9, ceph_frac=0.34, pyg_frac=0.10, W=0.30, thorax_w=0.36, thorax_w_back=0.26, pyg_w=0.15,
    ceph_p=1.6, ceph_q=1.4, pyg_p=1.5, pyg_q=1.2, dome=0.05, glab_front=0.10, glab_back=0.10, glab_h=0.04,
    glab_len=0.6, glab_furrows=0, axis_w=0.11, axis_h=0.06, eye="small", eye_x=0.20, eye_y=0.45, eye_size=0.8,
    genal_spine=0.0, pleural_tips=0.26, pyg_rings=2, pyg_ribs=1, tubercles=0, antenna=0.10,
    shell=(0.78, 0.60, 0.36), shell_light=(0.92, 0.80, 0.58), axis=(0.70, 0.50, 0.28), groove=(0.34, 0.22, 0.10),
    under=(0.66, 0.50, 0.32), leg=(0.70, 0.54, 0.34),
)
SPINE = (0.48, 0.32, 0.16)


def extras(mb):
    s = SPEC
    yf = -s.length / 2
    yb = s.length / 2
    yc = yf + s.length * s.ceph_frac
    gy = yf + (yc - yf) * 0.45

    def glab_col(co, n):
        c = s.shell
        if noise.noise(co * 40.0) > 0.35:
            c = s.shell_light
        return c
    mb.add(nh.uv_ellipsoid((0, gy, 0.08), (0.19, 0.20, 0.17), 20, 14), glab_col)
    # long genal spines curving out and back from the cheeks
    for sx in (-1, 1):
        b0 = Vector((sx * 0.20, yc - 0.06, 0.0))
        mb.add(nh.tube([b0, b0 + Vector((sx * 0.20, 0.02, -0.01)), b0 + Vector((sx * 0.34, 0.16, -0.02)),
                        b0 + Vector((sx * 0.38, 0.34, -0.03))], [0.030, 0.022, 0.012, 0.0], sides=6), SPINE)
        p0 = Vector((sx * 0.05, yb - 0.04, 0.01))
        mb.add(nh.tube([p0, p0 + Vector((sx * 0.06, 0.15, 0.0)), p0 + Vector((sx * 0.14, 0.36, -0.01))],
                       [0.025, 0.016, 0.0], sides=6), SPINE)
    # small eyes on the side of the glabella
    for sx in (-1, 1):
        a = math.radians(35)
        mb.add(nh.ellipsoid((sx * 0.18 * math.cos(a), gy + 0.06, 0.08 + 0.15 * math.sin(a) * 0.5),
                            (0.022, 0.022, 0.022), 2), s.eye_col)


if __name__ == "__main__":
    nh.run(lambda: ex.with_extras(lambda: tr.build(SPEC), extras), SPEC.name, **tr.VIEWS)
