"""
Procedural Conus geographus (the geography cone, a cone snail of Indo-Pacific coral
reefs, shell up to about 13-16 cm) for the map (Fixed style).

The most venomous cone snail, whose sting has killed people: it hunts small fish at
night by opening its mouth into a wide false "net" and firing a hollow, harpoon-like
radular tooth loaded with venom. Modelled crawling on the sand:
  * Shell: a thin, relatively broad cone, narrow end (the siphonal canal) pointing
    forward, a rounded shoulder crowned with a row of blunt knobs and a low, stepped
    spire at the back. A lathe shell whose cross-section is slightly flattened below.
  * Colours: pinkish white, covered with a fine brown-orange network ("tents" of
    white triangles), darker brown cloudy blotches and two broad, darker spiral bands.
  * Soft parts: a mottled grey-brown foot under the shell, a striped siphon raised
    from the front like a snorkel, two small eye stalks and the pink proboscis reaching
    forward along the sand with a white harpoon tooth at its tip.
Faces -Y, pivot on the ground (sole of the foot at z = 0).

Usage:
  blender --background --python tools/blender/conus_geographus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ConusGeographus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402

SHELL = (0.93, 0.85, 0.80)
NET = (0.62, 0.34, 0.16)
CLOUD = (0.45, 0.24, 0.12)
FOOT = (0.45, 0.40, 0.35)
FOOT_DARK = (0.25, 0.21, 0.18)
SIPHON = (0.80, 0.45, 0.20)
PROB = (0.88, 0.62, 0.60)
HARPOON = (0.96, 0.95, 0.90)
EYE = (0.03, 0.03, 0.03)

Y0, Y1, YA = -0.50, 0.24, 0.46       # front tip, shoulder, spire apex
R_SH = 0.24                           # shoulder radius
ZC = 0.20                             # shell axis height
KNOBS = 11


def radius(y):
    if y <= Y1:
        t = (y - Y0) / (Y1 - Y0)
        return 0.035 + (R_SH - 0.035) * (t ** 0.85)          # nearly straight-sided cone
    t = (y - Y1) / (YA - Y1)
    # rounded shoulder, then a low, concave, stepped spire to a pointed apex
    if t < 0.22:
        return R_SH * (1.0 - 0.3 * (t / 0.22) ** 2)
    k = (t - 0.22) / 0.78
    step = 0.012 * (math.sin(k * math.pi * 3.5) ** 2)
    return max(0.0, R_SH * 0.70 * (1.0 - k) ** 1.4 + step * (1.0 - k))


def shell():
    bm = bmesh.new()
    nseg = 64
    rings = []
    ys = [Y0 + (Y1 - Y0) * (i / 30) for i in range(30)] + [Y1 + (YA - Y1) * (i / 22) for i in range(23)]
    tipf = bm.verts.new((0, Y0 - 0.02, ZC))
    tipb = bm.verts.new((0, YA + 0.01, ZC))
    for y in ys[1:-1]:
        r = radius(y)
        ring = []
        for k in range(nseg):
            a = k / nseg * math.tau
            rr = r
            # knobbed shoulder (the coronation)
            sh = math.exp(-((y - (Y1 + 0.03)) / 0.03) ** 2)
            rr += 0.03 * sh * max(0.0, math.cos(a * KNOBS)) ** 2
            x, z = math.cos(a) * rr, math.sin(a) * rr
            if z < 0:
                z *= 0.82          # flatter underside, sits on the foot
            ring.append(bm.verts.new((x, y, ZC + z)))
        rings.append(ring)
    for k in range(nseg):
        j = (k + 1) % nseg
        bm.faces.new([tipf, rings[0][j], rings[0][k]])
        bm.faces.new([tipb, rings[-1][k], rings[-1][j]])
    for a, b in zip(rings, rings[1:]):
        for k in range(nseg):
            j = (k + 1) % nseg
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def shell_color(co, n):
    a = math.atan2(co.z - ZC, co.x)
    y = co.y
    c = SHELL
    # fine net with white "tents": cell borders of a stretched voronoi pattern
    dist, _ = noise.voronoi(Vector((math.cos(a) * 3.0, y * 9.0, math.sin(a) * 3.0)), distance_metric="DISTANCE")
    net = 1.0 - nh.smoothstep(0.05, 0.16, dist[1] - dist[0])
    c = nh.lerp(c, NET, 0.6 * net)
    # cloudy blotches and two darker spiral bands
    cl = noise.noise(Vector((math.cos(a) * 2.0, y * 5.0, math.sin(a) * 2.0)))
    band = max(math.exp(-((y + 0.22) / 0.07) ** 2), math.exp(-((y - 0.08) / 0.07) ** 2))
    c = nh.lerp(c, CLOUD, nh.smoothstep(0.0, 0.4, cl + 0.4 * band) * 0.8)
    if y > Y1 + 0.01:     # spire: paler with brown spots on the knobs
        c = nh.lerp(c, SHELL, 0.4)
    if co.z < ZC - 0.12 and abs(co.x) < 0.06 and y > Y0 + 0.05:   # the long, narrow aperture slit below
        c = (0.30, 0.18, 0.12)
    return c


def foot_color(co, n):
    k = max(0.0, noise.noise(co * 25.0))
    return nh.lerp(FOOT, FOOT_DARK, 0.7 * k)


def build():
    mb = nh.MeshBuilder()
    mb.add(shell(), shell_color)
    # foot: a broad flat sole under the shell, a little longer than it at the front
    foot = nh.ellipsoid((0, -0.10, 0.045), (0.17, 0.48, 0.05), subdivisions=3)
    mb.add(foot, foot_color)
    # head with eye stalks at the front
    mb.add(nh.ellipsoid((0, -0.55, 0.07), (0.07, 0.07, 0.045), subdivisions=2), foot_color)
    for sx in (-1, 1):
        base = Vector((sx * 0.04, -0.58, 0.09))
        tip = base + Vector((sx * 0.03, -0.06, 0.07))
        mb.add(nh.tube([tuple(base), tuple(tip)], [0.012, 0.008], sides=6), FOOT)
        mb.add(nh.ellipsoid(tuple(tip), (0.011,) * 3, subdivisions=1), EYE)
    # siphon raised like a snorkel from the front of the shell
    pts = [Vector((0, -0.46, 0.20)), Vector((0, -0.56, 0.27)), Vector((0, -0.62, 0.36)), Vector((0, -0.63, 0.42))]

    def siphon_col(co, n):
        band = 0.5 + 0.5 * math.sin(co.z * 70.0)
        return nh.lerp(SIPHON, (0.25, 0.14, 0.08), 0.7 * nh.smoothstep(0.6, 0.85, band))

    mb.add(nh.tube([tuple(p) for p in pts], [0.03, 0.026, 0.024, 0.03], sides=10, cap_end=False), siphon_col)
    # proboscis reaching forward along the sand, harpoon tooth at the tip
    pp = [Vector((0, -0.60, 0.05)), Vector((0.02, -0.72, 0.035)), Vector((0.0, -0.84, 0.03)), Vector((-0.01, -0.93, 0.03))]
    mb.add(nh.tube([tuple(p) for p in pp], [0.022, 0.017, 0.013, 0.011], sides=8), PROB)
    mb.add(nh.tube([(-0.01, -0.93, 0.03), (-0.012, -0.985, 0.032)], [0.005, 0.0], sides=5), HARPOON)
    obj = mb.to_object("ConusGeographus", roughness=0.35)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ConusGeographus", ground=(0.80, 0.74, 0.58), views=((35, 30), (-90, 8), (160, 30)))
