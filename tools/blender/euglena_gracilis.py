"""
Procedural low-poly Euglena gracilis (euglenid flagellate) for colony instancing.

A spindle-shaped green cell, blunt and rounded at the front and tapering to a short point at the
rear, swimming toward -Y. The flexible pellicle is drawn as faint helical strips spiralling
round the cell (slight ridges with paler grooves); many disc-shaped chloroplasts show as darker
green spots, a pale nucleus sits faintly in the middle, and two pale paramylon grains bulge
just through the surface. At the front a small dark reservoir pit opens, with the red-orange
eyespot (stigma) beside it, and one long flagellum trails out of the pit, beating in a gentle
wave. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/euglena_gracilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Euglena.fbx
Faces -Y (front), long axis along Y, ~1.6 units long including the flagellum. Pivot at the
centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

SEED = 9
HALF = 0.56           # half-length of the cell along Y
RADIUS = 0.115        # radius at the widest point
AROUND = 28
ALONG = 40
STRIPS = 14           # pellicle strips (half the vertices round, so they alternate)
TWIST = 1.1           # turns of a strip from the front to the back
CHLOROPLASTS = 48
CHLORO_R = 0.042

CELL = (0.62, 0.80, 0.34)        # pale yellow-green cytoplasm
CELL_REAR = (0.70, 0.78, 0.44)
CHLORO = (0.16, 0.46, 0.12)      # chloroplast discs
STRIP = (0.80, 0.90, 0.60)       # paler pellicle grooves
NUCLEUS = (0.78, 0.84, 0.60)
PIT = (0.20, 0.30, 0.14)
EYESPOT = (0.95, 0.30, 0.08)
PARAMYLON = (0.95, 0.95, 0.86)
FLAG = (0.86, 0.92, 0.80)


def profile(t):
    """Radius fraction along the cell (t = -1 front .. 1 rear): blunt front, pointed rear."""
    if t < -0.25:
        u = (t + 0.25) / 0.75                    # -1 .. 0
        return (1.0 - abs(u) ** 2.4) ** 0.5
    u = (t + 0.25) / 1.25                        # 0 .. 1
    return max(0.0, (1.0 - u ** 1.6)) ** 1.15 * (1.0 - 0.06 * u)


def body(rng):
    # chloroplast centres spread over the surface in (t, phi)
    spots = []
    tries = 0
    while len(spots) < CHLOROPLASTS and tries < 5000:
        tries += 1
        t = rng.uniform(-0.88, 0.78)
        phi = rng.uniform(0, math.tau)
        r = RADIUS * profile(t)
        if rng.random() > profile(t):           # keep the density even per unit area
            continue
        p = Vector((math.cos(phi) * r, t * HALF, math.sin(phi) * r))
        if all((p - s).length > CHLORO_R * 2.2 for s in spots):
            spots.append(p)

    bm = bmesh.new()
    vcol = {}
    rings = []
    for i in range(ALONG + 1):
        u = i / ALONG
        t = -math.cos(u * math.pi)               # denser toward the ends
        y = t * HALF
        if i == 0:                                # reservoir pit: the front pole sinks in
            v = bm.verts.new((0.0, y + 0.045, 0.012))
            vcol[v] = PIT
            rings.append([v])
            continue
        if i == ALONG:
            v = bm.verts.new((0.0, y, 0.0))
            vcol[v] = CELL_REAR
            rings.append([v])
            continue
        r0 = RADIUS * profile(t)
        ring = []
        for k in range(AROUND):
            phi = k / AROUND * math.tau
            stripe = 0.5 + 0.5 * math.cos(STRIPS * phi + TWIST * math.tau * t)
            r = r0 * (1.0 + 0.04 * stripe)
            co = Vector((math.cos(phi) * r, y, math.sin(phi) * r))
            near = min((co - s).length for s in spots)
            chl = 1.0 - nh.smoothstep(CHLORO_R * 0.45, CHLORO_R, near)
            co = Vector((math.cos(phi) * r * (1 + 0.04 * chl), y, math.sin(phi) * r * (1 + 0.04 * chl)))
            v = bm.verts.new(co)
            c = nh.lerp(CELL, CELL_REAR, nh.smoothstep(0.2, 1.0, t))
            c = nh.lerp(c, NUCLEUS, math.exp(-((t - 0.05) / 0.16) ** 2) * 0.5)
            c = nh.lerp(c, CHLORO, chl * (1.0 - nh.smoothstep(0.75, 0.95, t)))
            c = nh.lerp(c, STRIP, (1.0 - stripe) * 0.55)
            # the front lip darkens into the reservoir pit
            c = nh.lerp(c, PIT, (1.0 - nh.smoothstep(-0.99, -0.94, t)) * 0.7)
            vcol[v] = c
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(AROUND):
            j = (k + 1) % AROUND
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def surface(t, phi):
    r = RADIUS * profile(t)
    return Vector((math.cos(phi) * r, t * HALF, math.sin(phi) * r)), Vector((math.cos(phi), 0, math.sin(phi)))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    bm, vcol = body(rng)
    nf.add_colored(mb, bm, vcol)

    # red-orange eyespot beside the reservoir, on the upper side
    p, n = surface(-0.80, math.radians(70))
    mb.add(nh.ellipsoid(tuple(p - n * 0.012), (0.030, 0.024, 0.026), subdivisions=2), EYESPOT)
    # paramylon grains
    for t, phi, sz in ((0.10, math.radians(120), 0.040), (0.35, math.radians(40), 0.032)):
        p, n = surface(t, phi)
        mb.add(nh.ellipsoid(tuple(p - n * sz * 0.35), (sz * 0.8, sz * 1.3, sz * 0.8), subdivisions=2), PARAMYLON)

    # one long flagellum out of the reservoir pit, sweeping forward in a gentle wave
    base = Vector((0.0, -HALF + 0.03, 0.012))
    pts, radii = [], []
    n_pts = 18
    length = 0.62
    for k in range(n_pts):
        t = k / (n_pts - 1)
        y = -t * length
        x = 0.07 * math.sin(t * math.tau * 1.3) * t + 0.10 * t * t
        z = 0.03 * math.sin(t * math.tau * 1.3 + 1.0) * t
        pts.append(base + Vector((x, y, z)))
        radii.append(0.013 * (1.0 - 0.6 * t) if k < n_pts - 1 else 0.0)
    mb.add(nh.tube(pts, radii, sides=5), FLAG)

    obj = mb.to_object("Euglena", roughness=0.4)
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    for v in obj.data.vertices:
        for a in range(3):
            v.co[a] -= (lo[a] + hi[a]) / 2
    return obj


if __name__ == "__main__":
    nh.run(build, "Euglena", views=((35, 30), (-90, 10), (0, 85)))
