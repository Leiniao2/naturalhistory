"""
Procedural Takakkawia lineata (Middle Cambrian sponge, Burgess Shale, British Columbia; Walcott,
1920, named after Takakkaw Falls in Yoho National Park) for the map: a small, elongate conical
sponge rising from a sharp root tip, its wall carrying four (tetraradial) columns of spicule
tracts, each split into two stiff, blade-like fins that run the length of the body, so eight
fins project radially. Each column is capped by an enlarged marginal spicule at the flaring
osculum. Up to about 4 cm tall.

The fins are built of overlapping flanges, drawn as a saw-toothed outer edge with a fine ring
banding; the wall between the columns shows faint horizontal "ladder" bundles of spicules. The
fins are offset 45 degrees from the front so a front view shows the tetraradial cross clearly.
The root tip sits in a small mound of dark mud. Pale cream fins over a tan body with a dark
osculum; the living colour is unknown.
Fixed style: pivot at the base (z = 0), upright.

Usage:
  blender --background --python tools/blender/takakkawia_lineata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Takakkawia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_vauxia as nv  # noqa: E402  (mud_patch)

SEED = 9
HEIGHT = 1.45
Z0 = 0.03            # root tip height (inside the mud mound)
SIDES = 32
RINGS = 26
WALL = 0.02
INNER = 0.25         # fraction of the height visible as open cavity
COLUMNS = 4
SPLIT = math.radians(10)   # half-angle between the two fins of a column
FIN_T = 0.014        # fin thickness
TEETH = 13           # overlapping flanges along each fin

BODY = (0.70, 0.58, 0.40)
SHADE = (0.50, 0.40, 0.27)
LADDER = (0.84, 0.76, 0.58)
FIN = (0.92, 0.87, 0.74)
FIN_EDGE = (0.98, 0.96, 0.90)
FIN_LINE = (0.66, 0.58, 0.44)
VENT = (0.18, 0.13, 0.09)
RIM = (0.90, 0.84, 0.70)
MOUND = (0.34, 0.31, 0.27)


def radius(t):
    """Body radius at height fraction t: sharp root tip -> slender cone -> flaring osculum."""
    return 0.004 + 0.15 * nh.smoothstep(0.0, 1.0, t) ** 0.6 * (0.55 + 0.45 * t) \
        + 0.07 * nh.smoothstep(0.78, 1.0, t) ** 2


def fin_width(t):
    """Radial projection of a fin beyond the wall."""
    return 0.12 * nh.smoothstep(0.02, 0.3, t) * (1.0 - 0.25 * t) * (1.0 - 0.5 * nh.smoothstep(0.92, 1.0, t))


def z_of(t):
    return Z0 + HEIGHT * t


def body(warp):
    bm = bmesh.new()
    rings = []
    for i in range(RINGS + 1):
        t = i / RINGS
        r = radius(t)
        z = z_of(t)
        rings.append([bm.verts.new((math.cos(k / SIDES * math.tau) * r, math.sin(k / SIDES * math.tau) * r, z))
                      for k in range(SIDES)])
    # rounded lip
    r1, z1 = radius(1.0), z_of(1.0)
    for i in range(1, 4):
        a = i / 4 * math.pi
        rr = r1 - WALL * 0.5 * (1 - math.cos(a))
        zz = z1 + WALL * 0.6 * math.sin(a)
        rings.append([bm.verts.new((math.cos(k / SIDES * math.tau) * rr, math.sin(k / SIDES * math.tau) * rr, zz))
                      for k in range(SIDES)])
    n_in = max(3, round(INNER * RINGS))
    for i in range(RINGS, RINGS - n_in - 1, -1):
        t = i / RINGS
        r = max(0.006, radius(t) - WALL)
        rings.append([bm.verts.new((math.cos(k / SIDES * math.tau) * r, math.sin(k / SIDES * math.tau) * r, z_of(t)))
                      for k in range(SIDES)])
    for a, b in zip(rings, rings[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        t = max(0.0, min(1.0, (co.z - Z0) / HEIGHT))
        r = math.hypot(co.x, co.y)
        if r < radius(t) - WALL * 0.5:
            return VENT
        c = nh.lerp(SHADE, BODY, nh.smoothstep(0.0, 0.4, t))
        c = nh.lerp(c, LADDER, 0.5 * math.cos(t * HEIGHT * 75) ** 6 * nh.smoothstep(0.08, 0.25, t))
        c = nh.lerp(c, SHADE, 0.2 * nh.smoothstep(0.1, -0.4, noise.noise(co * 6 + warp)))
        return nh.lerp(c, RIM, nh.smoothstep(0.985, 1.0, t))
    return bm, color


def fin(phi, rng):
    """One blade-like fin at azimuth phi: a thin slab from inside the wall out to a saw-toothed
    outer edge (overlapping flanges), from just above the root tip to just below the rim."""
    e = Vector((math.cos(phi), math.sin(phi), 0.0))
    g = Vector((-math.sin(phi), math.cos(phi), 0.0)) * (FIN_T * 0.5)
    t0, t1 = 0.03, 0.97
    ts, ws = [], []
    dt = (t1 - t0) / TEETH
    for k in range(TEETH):
        a = t0 + k * dt
        ts += [a + 0.02 * dt, a + 0.9 * dt]
        ws += [0.86, 1.0]
    ts.append(t1)
    ws.append(0.6)
    bm = bmesh.new()
    quads = []
    for t, w in zip(ts, ws):
        z = z_of(t)
        inner = e * max(0.002, radius(t) - WALL * 0.5) + Vector((0, 0, z))   # inside the wall
        outer = e * (radius(t) + fin_width(t) * w * rng.uniform(0.95, 1.05)) + Vector((0, 0, z + 0.012 * w))
        quads.append([bm.verts.new(inner + g), bm.verts.new(outer + g),
                      bm.verts.new(outer - g), bm.verts.new(inner - g)])
    for a, b in zip(quads, quads[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(quads[0])))
    bm.faces.new(quads[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        t = max(0.0, min(1.0, (co.z - Z0) / HEIGHT))
        d = co.to_2d().length - radius(t)
        f = (t - t0) / dt
        c = nh.lerp(FIN, FIN_EDGE, nh.smoothstep(0.03, 0.12, d))
        # dark line at each flange boundary (concentric-ring banding of the blades)
        c = nh.lerp(c, FIN_LINE, 0.6 * nh.smoothstep(0.25, 0.0, abs(f - round(f))) * nh.smoothstep(0.0, 0.04, d))
        return c
    return bm, color


def marginal_spicule(phi, rng):
    """Enlarged spicule capping a column, rising from the rim and leaning outward."""
    e = Vector((math.cos(phi), math.sin(phi), 0.0))
    base = e * (radius(0.93) + 0.02) + Vector((0, 0, z_of(0.9)))
    d = (Vector((0, 0, 1)) + e * rng.uniform(0.25, 0.4)).normalized()
    length = rng.uniform(0.28, 0.36)
    pts = [base, base + d * length * 0.5, base + d * length]
    bm = nh.tube(pts, [0.016, 0.011, 0.0], sides=6)
    return bm, lambda co, n: nh.lerp(FIN, FIN_EDGE, min(1.0, (co - base).length / length + 0.2))


def build():
    rng = random.Random(SEED)
    warp = Vector((rng.random() * 30, rng.random() * 30, rng.random() * 30))
    mb = nh.MeshBuilder()
    mb.add(*body(warp))
    for c in range(COLUMNS):
        phi = math.radians(45) + c / COLUMNS * math.tau
        for s in (-1, 1):
            mb.add(*fin(phi + s * SPLIT, rng), smooth=False)
        mb.add(*marginal_spicule(phi, rng))
    # small mound of mud holding the root tip
    mb.add(nh.ellipsoid((0, 0, 0.0), (0.12, 0.11, 0.05), subdivisions=2,
                        deform=lambda n: 1.0 + 0.12 * noise.noise(n * 2.5 + warp)), MOUND)
    nv.mud_patch(mb, rng, 0.25, 0.45, count=6, size=(0.035, 0.065))
    obj = mb.to_object("Takakkawia", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Takakkawia", ground=(0.40, 0.38, 0.34), views=((0, 15), (60, 30), (10, 80)))
