"""
Procedural Meganeuropsis permiana (Early Permian griffinfly, ~70 cm wingspan) in level flight,
for map colonies.

The largest insect known, a Permian successor of Meganeura from Elmo, Kansas: built on
meganeura_monyi.py (same body plan - huge eyes, boxy thorax, long ringed abdomen, spiny
catching legs) but with longer, narrower wings and a longer, slimmer abdomen, and coloured
differently: a metallic bronze-green body with pale rings, and smoky wings with amber bases
and dark tips. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/meganeuropsis_permiana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Meganeuropsis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import meganeura_monyi as mg  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Meganeuropsis"
mg.BODY = (0.12, 0.17, 0.10)
mg.BODY_DARK = (0.05, 0.07, 0.04)
mg.STRIPE = (0.72, 0.70, 0.50)
mg.EYE = (0.16, 0.10, 0.06)
mg.EYE_SHEEN = (0.46, 0.32, 0.18)
mg.MEMBRANE = (0.56, 0.56, 0.54)
mg.MEMBRANE_ROOT = (0.70, 0.48, 0.20)
mg.VEIN = (0.10, 0.08, 0.06)
mg.ABD_LEN = 0.74


def build():
    mb = nh.MeshBuilder()
    mg.build_head(mb)
    mg.build_thorax(mb)
    mg.build_abdomen(mb)
    mg.build_legs(mb)
    fore = mg.build_wing(0.90, 0.100, 0.100, 6, 24, 3)
    hind = mg.build_wing(0.86, 0.105, 0.175, 6, 24, 4)
    for mirror in (False, True):
        mg.place([(bm.copy(), c) for bm, c in fore], mb, mirror,
                 hinge=(0.025, -0.300, 0.095), sweep_deg=-3, dihedral_deg=4)
        mg.place([(bm.copy(), c) for bm, c in hind], mb, mirror,
                 hinge=(0.025, -0.225, 0.090), sweep_deg=6, dihedral_deg=3)
    for bm, _ in fore + hind:
        bm.free()
    obj = mb.to_object(NAME, roughness=0.4)
    centre = Vector((0.0, (mg.HEAD.y - 0.08 + mg.ABD_START.y + mg.ABD_LEN + 0.07) / 2, 0.03))
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
