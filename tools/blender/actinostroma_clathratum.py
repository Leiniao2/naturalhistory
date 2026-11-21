"""
Procedural Actinostroma clathratum (Devonian stromatoporoid sponge, a main reef builder of
the Devonian seas, Europe and North America) for the map (Fixed style).

A massive, domed, layered mound often 30 cm to a metre across: the calcareous skeleton grew
in thin sheets laid one over another, so the flanks show stacked, slightly overhanging
growth layers (latilaminae) like a pile of pancakes. The upper surface is dotted with small,
regularly spaced bumps (mamelons), each the centre of a starry pattern of branching grooves
(astrorhizae), the canals that carried water to the living tissue. Cream to buff, with
darker layer lines (colour conjectural). Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/actinostroma_clathratum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Actinostroma.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.90, 0.84, 0.68)
LAYER = (0.62, 0.48, 0.30)
LINE = (0.34, 0.24, 0.14)
STAR = (0.52, 0.42, 0.30)
MAMELON = (0.96, 0.92, 0.80)

RX, RY, RZ = 0.80, 0.70, 0.42
LAYERS = 9
SPACING = 0.16


def mamelons():
    pts = []
    for i in range(-6, 7):
        for j in range(-6, 7):
            x = (i + 0.5 * (j % 2)) * SPACING
            y = j * SPACING * 0.87
            jit = noise.noise(Vector((i * 1.3, j * 1.7, 0.5))) * 0.03
            pts.append(Vector((x + jit, y - jit, 0)))
    return pts


MAM = mamelons()


def nearest_mamelon(co):
    best, bp = 9.0, None
    for p in MAM:
        d = math.hypot(co.x - p.x, co.y - p.y)
        if d < best:
            best, bp = d, p
    return best, bp


def height(x, y):
    """Terraced dome: smooth on top, stepped growth sheets on the flanks."""
    r = min(1.0, math.hypot(x / RX, y / RY)) * (1.0 - 0.04 * (0.5 + 0.5 * noise.noise(Vector((x * 2.5, y * 2.5, 0.7)))))
    if r >= 1.0:
        return 0.0, r
    z = RZ * (1.0 - r ** 2) ** (1 / 2.2)
    flank = nh.smoothstep(0.35, 0.65, r)
    q = z / (RZ / LAYERS)
    terr = (math.floor(q) + nh.smoothstep(0.55, 1.0, q % 1.0)) * (RZ / LAYERS)
    return z + (terr - z) * flank * 0.9, r


def build():
    import bmesh
    mb = nh.MeshBuilder()
    # polar grid (dense towards the rim, where the growth sheets step down)
    bm = bmesh.new()
    NA, NR = 96, 64
    centre = bm.verts.new((0, 0, 0))
    rings = []
    for i in range(1, NR + 1):
        t = i / NR
        rf = 1.0 - (1.0 - t) ** 1.6
        ring = []
        for j in range(NA):
            a = j / NA * math.tau
            x, y = math.cos(a) * RX * rf, math.sin(a) * RY * rf
            z, r = height(x, y)
            d, _p = nearest_mamelon(Vector((x, y, 0)))
            z += 0.026 * math.exp(-(d / 0.03) ** 2) * (1 - nh.smoothstep(0.45, 0.7, r))
            ring.append(bm.verts.new((x, y, max(z, 0.0) if i < NR else 0.0)))
        rings.append(ring)
    _z, _r = height(0, 0)
    centre.co.z = _z
    for j in range(NA):
        bm.faces.new([centre, rings[0][j], rings[0][(j + 1) % NA]])
    for a, b in zip(rings, rings[1:]):
        for j in range(NA):
            k = (j + 1) % NA
            bm.faces.new([a[j], b[j], b[k], a[k]])
    bmesh.ops.triangulate(bm, faces=bm.faces)

    def color(co, n):
        r = math.hypot(co.x / RX, co.y / RY)
        c = TOP
        flank = nh.smoothstep(0.35, 0.65, r)
        q = (co.z / (RZ / LAYERS)) % 1.0
        c = nh.lerp(c, LAYER, flank * (1 - n.z) * 1.4 if n.z < 1 else 0)
        c = nh.lerp(c, LINE, flank * nh.smoothstep(0.75, 0.25, n.z) * 0.8)
        if r < 0.7:
            d, p = nearest_mamelon(co)
            a = math.atan2(co.y - p.y, co.x - p.x)
            star = nh.smoothstep(0.7, 0.97, 0.5 + 0.5 * math.cos(a * 6 + d * 25)) * nh.smoothstep(0.075, 0.02, d)
            w = 1 - nh.smoothstep(0.45, 0.7, r)
            c = nh.lerp(c, STAR, 0.75 * star * w)
            c = nh.lerp(c, MAMELON, nh.smoothstep(0.022, 0.0, d) * w)
        st = noise.noise(Vector((co.x * 3 + 7, co.y * 3, co.z * 3))) * 0.5 + 0.5
        return tuple(min(1.0, x * (0.9 + 0.15 * st)) for x in c)
    mb.add(bm, color)
    return ec.ground(mb.to_object("Actinostroma", roughness=0.8))


if __name__ == "__main__":
    ec.export(build, "Actinostroma", fixed=True)
