"""
Procedural Triamyxa coprolithica (Late Triassic myxophagan beetle, ~1.5 mm) for map colonies.

A tiny beetle from Krasiejów in Poland, found perfectly preserved in three dimensions
inside a fossil dropping, probably of the dinosaur relative Silesaurus that swallowed it by
accident: a short, very convex, oval, shiny dark body with the elytra closed over the back,
a small head with clubbed antennae and short legs. Like its living relatives it likely
grazed algae on damp surfaces at the water's edge. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Triamyxa.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402

SHELL = (0.16, 0.10, 0.06)
SHINE = (0.46, 0.30, 0.16)
HEAD = (0.12, 0.08, 0.05)
LEG = (0.42, 0.28, 0.14)
EYE = (0.02, 0.02, 0.02)
BASE = 0.06


def elytra_col(co, n):
    c = nh.lerp(SHELL, SHINE, 0.6 * nh.smoothstep(0.5, 0.95, n.z) * nh.smoothstep(0.05, -0.15, co.y))
    if abs(co.x) < 0.008 and co.y > -0.15:          # elytral suture
        c = nh.lerp(c, (0.05, 0.03, 0.02), 0.8)
    # fine rows of punctures
    k = 0.5 + 0.5 * math.sin(co.x * 120.0)
    return nh.lerp(c, (0.08, 0.05, 0.03), 0.3 * nh.smoothstep(0.85, 1.0, k))


def build():
    mb = nh.MeshBuilder()
    # convex oval body: elytra + pronotum
    el = nh.uv_ellipsoid((0, 0.05, BASE + 0.02), (0.30, 0.40, 0.24), 28, 16)
    for v in el.verts:
        if v.co.z < BASE + 0.02:
            v.co.z = BASE + 0.02 - (BASE + 0.02 - v.co.z) * 0.25
    mb.add(el, elytra_col)
    pro = nh.uv_ellipsoid((0, -0.33, BASE + 0.03), (0.24, 0.12, 0.15), 20, 10)
    mb.add(pro, lambda co, n: nh.lerp(HEAD, SHINE, 0.4 * nh.smoothstep(0.6, 0.95, n.z)))
    hc = Vector((0, -0.45, BASE + 0.02))
    mb.add(nh.uv_ellipsoid(hc, (0.13, 0.08, 0.08), 12, 8), HEAD)
    for s in (-1, 1):
        mb.add(nh.ellipsoid(hc + Vector((s * 0.10, -0.01, 0.02)), (0.035, 0.04, 0.035), 1), EYE)
        # clubbed antennae
        a0 = hc + Vector((s * 0.08, -0.05, 0.0))
        tip = a0 + Vector((s * 0.12, -0.12, 0.02))
        mb.add(nh.tube([a0, tip], [0.012, 0.010], sides=5), LEG)
        mb.add(nh.ellipsoid(tip, (0.03, 0.035, 0.025), 1), HEAD)
        # six short legs
        for y, fy in ((-0.30, -0.42), (-0.10, -0.02), (0.10, 0.25)):
            hip = Vector((s * 0.14, y, BASE))
            knee = Vector((s * 0.30, (y + fy) * 0.5, BASE + 0.02))
            foot = Vector((s * 0.38, fy, 0.0))
            mb.add(nh.tube([hip, knee, foot], [0.022, 0.016, 0.008], sides=5), LEG)
    obj = mb.to_object("Triamyxa", roughness=0.25)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.3f}, hip {BASE:.3f} -> mapHip {BASE / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "Triamyxa", ground=(0.36, 0.40, 0.22), views=((35, 30), (0, 80), (-90, 10)))
