"""
Procedural Chelotriton paradoxus (Europe, late Oligocene to Miocene, ~25-15 Ma) for map colonies:
a crocodile newt (Salamandridae), about 15-20 cm long.

A broad-headed, stocky newt with rough, warty skin, a row of knobs along the
back and, along each flank, the pointed tips of its long ribs, which in living
crocodile newts can pierce the skin to deliver toxic secretions; a flattened
swimming tail. Shown dark brown-black with orange rib knobs, head ridges and
underside (like its living relatives Tylototriton and Echinotriton).
Built with nh_car_tetrapod.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/chelotriton_paradoxus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChelotritonParadoxus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_tetrapod as tp  # noqa: E402
from mathutils import Vector  # noqa: E402

ORANGE = (0.85, 0.42, 0.10)


def warts(sp, spine):
    """Orange rib-tip knobs along both flanks, a dark knobbed ridge down the back."""
    out = []
    s0, s1 = spine.s_neck + sp.trunk_len * 0.05, spine.s_trunk - sp.trunk_len * 0.05
    n = 9
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1)
        p = spine.at(s)
        rx, rz = spine.rx(s), spine.rz(s)
        for sx in (-1, 1):
            out.append((nh.ellipsoid(tuple(p + Vector((sx * rx * 0.98, 0, rz * 0.15))), (0.013, 0.013, 0.012),
                                     subdivisions=2), ORANGE))
        out.append((nh.ellipsoid(tuple(p + Vector((0, 0, rz * 0.95))), (0.012, 0.016, 0.011), subdivisions=2),
                    (0.12, 0.08, 0.05)))
    # swollen, orange glandular bosses at the back corners of the broad head
    for sx in (-1, 1):
        p = spine.at(sp.head_len * 0.88)
        out.append((nh.ellipsoid(tuple(p + Vector((sx * spine.rx(sp.head_len * 0.88) * 0.8, 0, sp.head_h * 0.55))),
                                 (0.018, 0.024, 0.012), subdivisions=2), ORANGE))
    return out


SPEC = tp.Spec(
    name="ChelotritonParadoxus",
    head_len=0.17, head_w=0.085, head_h=0.03, snout=0.7,
    neck_len=0.03, neck_r=0.06,
    trunk_len=0.42, trunk_r=0.065, trunk_h=0.75,
    tail_len=0.5, tail_r=0.04, tail_fin=1.9, tail_curve=0.1,
    leg_r=0.016, front=(0.07, 0.07), hind=(0.075, 0.075), foot=0.04, toes=4,
    back=(0.13, 0.10, 0.08), flank=(0.20, 0.15, 0.11), belly=(0.80, 0.45, 0.15),
    pattern="spots", pattern_col=(0.08, 0.06, 0.05), pattern_scale=1.4,
    head_col=(0.16, 0.12, 0.09), iris=(0.80, 0.50, 0.12), eye_r=0.017, eye_at=0.6, eye_up=0.7, teeth=0,
    voxel=0.006, max_tris=6000, extra=[warts],
)

if __name__ == "__main__":
    tp.run(SPEC)
