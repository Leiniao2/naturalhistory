"""
Procedural Bunodes lunula (Late Silurian synziphosurine, an early horseshoe-crab relative
of the Baltic region, a few centimetres long) for map colonies (Swim style).

A broad, vaulted, crescent-shaped head shield (lunula = "little moon") with radiating
hump-like ridges and tubercles and a small median eye mound; a wide opisthosoma of
free, tuberculate segments tapering into a narrow three-segmented postabdomen and a
spike-like telson. Low, shovel-like body for ploughing into soft mud. Greenish grey-
brown with pale tubercles. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the
body centre.

Usage:
  blender --background --python tools/blender/bunodes_lunula.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BunodesLunula.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402
import nh_sil_extra as ex  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="BunodesLunula",
    y_front=-0.66, y_pro=-0.16, pro_wf=0.40, pro_wb=0.44, pro_round=0.95, pro_h=0.10,
    pre_len=0.42, pre_w=[0.36, 0.34, 0.30, 0.25, 0.20, 0.15], pre_h=0.06,
    post_len=0.22, post_w=[0.07, 0.06, 0.05], post_round=0.8,
    telson="spike", telson_len=0.40, telson_w=0.028,
    eye="tubercle", eye_y=0.30, eye_size=1.0, chelicera="small", tubercles=1.0,
    legs=[L(0.30, 0.20, -50, 1, 0.02, 0.014), L(0.45, 0.22, -30, 1, 0.02, 0.015),
          L(0.60, 0.23, -10, 1, 0.02, 0.015), L(0.75, 0.24, 15, 1, 0.02, 0.016),
          L(0.90, 0.23, 35, 1, 0.02, 0.016)],
    shell=(0.40, 0.40, 0.30), shell_dark=(0.22, 0.22, 0.16), rim=(0.70, 0.68, 0.54),
    under=(0.64, 0.60, 0.48), leg=(0.52, 0.48, 0.36), leg_dark=(0.32, 0.30, 0.22),
)


def ridges(mb):
    """Radiating hump-like ridges on the head shield."""
    b = eu.Body(SPEC)
    cy = SPEC.y_front + b.L * 0.58
    for k in range(12):
        a = math.radians(-90 + 15 + k * 30)
        pts = []
        for t in (0.18, 0.40, 0.62, 0.82, 0.95):
            x = math.cos(a) * 0.40 * t
            y = cy + math.sin(a) * b.L * 0.58 * t
            if y < SPEC.y_front + 0.03 or y > SPEC.y_pro - 0.03:
                break
            if abs(x) > b.pro_w(y) * 0.92:
                break
            pts.append(Vector((x, y, b.pro_height(x, y) + 0.004)))
        if len(pts) >= 2:
            mb.add(nh.tube(pts, [0.02] * (len(pts) - 1) + [0.0], sides=6, scale_xy=(1.0, 0.7)),
                   nh.lerp(SPEC.shell, SPEC.shell_dark, 0.55))


if __name__ == "__main__":
    nh.run(lambda: ex.with_extras(lambda: eu.build(SPEC), ridges), SPEC.name, **eu.VIEWS)
