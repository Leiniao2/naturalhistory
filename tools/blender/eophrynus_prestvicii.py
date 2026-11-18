"""
Procedural Eophrynus prestvicii (Late Carboniferous coal measures of England, an armoured
trigonotarbid arachnid about 2 cm long) for map colonies (Ground style).

A spider-like arachnid without silk or venom, built like a little tank: a subtriangular
carapace with a median eye tubercle, eight walking legs and a broad, rounded, flattened
opisthosoma whose plates are covered in coarse tubercles, its rear margin drawn out into a
row of stout spines. Dark chocolate-brown with pale tubercles.
Built with nh_sil_eurypterid (the extra rear spines are added here). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eophrynus_prestvicii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eophrynus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402
from mathutils import Vector  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="Eophrynus",
    mode="ground", leg_lift=0.09,
    y_front=-0.50, y_pro=-0.17, pro_wf=0.07, pro_wb=0.21, pro_round=0.25, pro_h=0.06,
    pre_len=0.60, pre_w=[0.27, 0.30, 0.31, 0.30, 0.27, 0.22, 0.16, 0.10], pre_h=0.075,
    post_len=0.0, post_w=[], telson="none", telson_len=0.0,
    eye="tubercle", eye_y=0.30, eye_size=1.1, chelicera="small", body_dark_line=True, tubercles=0.85,
    legs=[L(0.10, 0.26, -60, 0, 0, 0.02), L(0.30, 0.48, -40, 0, 0, 0.024), L(0.50, 0.52, -15, 0, 0, 0.024),
          L(0.70, 0.52, 15, 0, 0, 0.024), L(0.90, 0.58, 45, 0, 0, 0.025)],
    shell=(0.24, 0.15, 0.09), shell_dark=(0.11, 0.07, 0.04), rim=(0.70, 0.58, 0.40),
    under=(0.36, 0.26, 0.17), leg=(0.32, 0.22, 0.13), leg_dark=(0.20, 0.13, 0.08),
)
SPIKE = (0.62, 0.50, 0.34)


def build():
    s = SPEC
    b = eu.Body(s)
    mb = nh.MeshBuilder()
    bm, col = eu.prosoma(b)
    mb.add(bm, col)
    prev = eu.preabdomen(mb, b)
    mb.add(eu.tail(b, prev), None)
    mb.add(nh.uv_ellipsoid((0, s.y_pro - b.L * 0.2, -0.035), (0.06, b.L * 0.3, 0.018), 10, 6), s.under)
    eu.legs(mb, b)
    eu.chelicerae(mb, b)
    eu.eyes(mb, b)
    # rear margin spines and big dorsal tubercles
    y_end = s.y_pro + s.pre_len
    for k in range(5):
        a = math.radians(-50 + 25 * k)
        base = Vector((math.sin(a) * 0.12, y_end - 0.08 + 0.05 * math.cos(a), 0.02))
        tip = base + Vector((math.sin(a) * 0.06, 0.09 * math.cos(a), 0.03))
        mb.add(nh.tube([base, tip], [0.022, 0.0], sides=6), SPIKE, smooth=False)
    for i in range(5):
        y = s.y_pro + s.pre_len * (0.12 + 0.17 * i)
        w = s.pre_w[min(len(s.pre_w) - 1, int((0.12 + 0.17 * i) * len(s.pre_w)))]
        for x in (-0.5, 0.0, 0.5):
            mb.add(nh.ellipsoid((x * w, y, s.pre_h * (0.95 - 0.5 * x * x)), (0.018, 0.018, 0.014), 1), SPIKE)
    obj = mb.to_object(s.name, roughness=0.5)
    nh.ground_to_zero(obj)
    vs = obj.data.vertices
    ys = [v.co.y for v in vs]
    off = -(min(ys) + max(ys)) / 2
    for v in vs:
        v.co.y += off
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, **eu.GROUND_VIEWS)
