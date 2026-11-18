"""
Procedural Stylonurus powriensis for the map: a large stylonurine eurypterid ("sea
scorpion") from the Early Devonian (Lochkovian, about 415 million years ago) of
Scotland, over a metre long.

Unlike the swimming pterygotids it had no swimming paddles: it was a stilt-legged
walker of the bottom. A raised, rounded, near-semicircular head shield with the eyes set
close together near its centre; small chelicerae; four pairs of long, slender, spineless
walking legs, the last two pairs enormously long and reaching far behind the body; a
slender segmented abdomen; and a long, thin, spike-like telson.

Built with nh_sil_eurypterid.py in its walking (ground) pose, then re-centred for the
Swim style. Colours are unknown: muted grey-brown with paler segment rims. Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/stylonurus_powriensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Stylonurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="Stylonurus",
    mode="ground", leg_lift=0.16,
    y_front=-0.62, y_pro=-0.30, pro_wf=0.20, pro_wb=0.22, pro_round=0.75, pro_h=0.085,
    pre_len=0.48, pre_w=[0.19, 0.20, 0.20, 0.19, 0.17, 0.14, 0.11], pre_h=0.06,
    post_len=0.40, post_w=[0.075, 0.068, 0.062, 0.056, 0.052], post_round=0.8,
    telson="spike", telson_len=0.50, telson_w=0.022,
    eye="kidney", eye_x=0.26, eye_y=0.50, eye_size=0.9, chelicera="small",
    legs=[L(0.15, 0.34, -55, 0, 0.0, 0.016), L(0.35, 0.42, -30, 0, 0.0, 0.018),
          L(0.60, 0.95, 40, 0, 0.0, 0.022), L(0.85, 1.10, 62, 0, 0.0, 0.024)],
    shell=(0.34, 0.30, 0.25), shell_dark=(0.18, 0.16, 0.13), rim=(0.64, 0.58, 0.48),
    under=(0.56, 0.50, 0.40), leg=(0.40, 0.34, 0.27), leg_dark=(0.24, 0.20, 0.16), spine=(0.70, 0.62, 0.50),
)


def build():
    obj = eu.build(SPEC)
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    xs = [v.co.x for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, 0, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, **eu.VIEWS)
