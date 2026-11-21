"""
Procedural Lithornis celetius (late Paleocene, ~60-56 Ma, North America) for map colonies.
Built with nh_pal_bird.py.

A lithornithid: one of the oldest palaeognath birds, relatives of ostriches, emus and
tinamous that could still fly. About 40 cm long and built much like a living tinamou:
a plump body, short tail, short neck, small head and a long, narrow, slightly
down-curved bill that it probed into soft ground for insects and worms. Plumage (unknown):
mottled and barred brown like a tinamou, paler buff below.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lithornis_celetius.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LithornisCeletius.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_bird as nb  # noqa: E402
from mathutils import noise  # noqa: E402

SPEC = nb.Spec(
    name="LithornisCeletius",
    body=(0.2, 0.34, 0.22), body_z=0.52, body_pitch=-8,
    neck_len=0.22, neck_r=0.06, neck_lean=30, head_r=0.075,
    beak_len=0.26, beak_h=0.04, beak_w=0.03, beak_hook=0.0,
    leg_len=0.4, leg_r=0.024, thigh_r=0.07, toe_len=0.1,
    wing=0.34, tail=0.07,
    plumage=(0.50, 0.38, 0.24), back=(0.36, 0.26, 0.16), wing_col=(0.40, 0.29, 0.18), head_col=(0.46, 0.36, 0.24),
    beak_col=(0.30, 0.26, 0.20), leg_col=(0.55, 0.50, 0.40), eye_r=0.014, shaggy=0.4,
    voxel=0.009, max_tris=9000, ground=(0.40, 0.42, 0.28),
)

DARK = (0.18, 0.12, 0.07)
BUFF = (0.80, 0.68, 0.48)


def build():
    obj = nb.build(SPEC)
    me = obj.data
    col = me.color_attributes["Col"]
    top = max(v.co.z for v in me.vertices)
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index]
            p, n = v.co, v.normal
            c = tuple(col.data[li].color_srgb[:3])
            # leave beak, legs and eyes alone: only the feathered body above the legs
            if p.z < SPEC.leg_len * 0.75 or abs(c[0] - SPEC.beak_col[0]) < 0.02 and abs(c[1] - SPEC.beak_col[1]) < 0.02:
                continue
            if max(c) < 0.12 or (c[0] > 0.8 and c[1] > 0.6 and c[2] < 0.4):
                continue
            c = nh.lerp(c, BUFF, 0.6 * nh.smoothstep(-0.1, -0.7, n.z))
            bar = 0.5 + 0.5 * noise.noise((p.x * 30, p.y * 55, p.z * 30))
            c = nh.lerp(c, DARK, 0.7 * nh.smoothstep(0.52, 0.66, bar) * nh.smoothstep(-0.3, 0.3, n.z))
            spot = noise.noise((p.x * 70, p.y * 70, p.z * 70))
            c = nh.lerp(c, BUFF, 0.45 * nh.smoothstep(0.45, 0.6, spot) * nh.smoothstep(0.0, 0.5, n.z))
            col.data[li].color_srgb = (c[0], c[1], c[2], 1.0)
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, ground=SPEC.ground, views=((35, 20), (-90, 5), (150, 35)))
