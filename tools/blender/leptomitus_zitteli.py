"""
Procedural Leptomitus zitteli (early Cambrian protomonaxonid demosponge, Parker Slate, Vermont)
for the map: one tall, slender, thin-walled tube rising from a small rounded holdfast on a
little patch of dark mud, its open top crowned by a fringe of protruding spicules.

The species is an elongate tubular sponge: the lectotype is about 7 cm long and narrows from
about 10 mm to 2 mm along its length, and a later specimen reaches 12 cm while only 2-4 mm
wide. Here the tube widens from a narrow base to the osculum at roughly the lectotype's
proportions (about 1:8). Its skeleton is an outer layer of coarse, parallel oxea spicules
running virtually the whole length of the sponge over an inner layer of tiny horizontal
spicules; that is drawn as fine longitudinal ribs (raised, paler spicule bundles) with faint
transverse banding between them. The lectotype shows a plumose (feathery) spray of spicules at
the distal end, drawn as thin needles flaring out of the rim. The tube is a single smooth
parametric surface (outer ribbed wall, a lip, and the inner wall down into the spongocoel),
gently curved. Pale straw-cream with glassy spicule highlights and a dark interior; the living
colour is unknown. Fixed style: pivot at the base (z = 0), upright so the map can sway it.

Usage:
  blender --background --python tools/blender/leptomitus_zitteli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LeptomitusZitteli.fbx
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

SEED = 5
HEIGHT = 1.75
R_BASE, R_TOP = 0.035, 0.115     # narrow base -> wide osculum
WALL = 0.018
SIDES = 36                       # around the tube
RINGS = 40                       # along the tube
RIBS = 14                        # coarse longitudinal oxea bundles
RIB_DEPTH = 0.08                 # as a fraction of the radius
INNER_DEPTH = 0.28               # fraction of the height visible as open spongocoel
NEEDLES = 30                     # plumose spicule fringe at the rim
BEND = 0.12                      # sideways sway of the tip

STRAW = (0.90, 0.78, 0.52)       # body
SHADE = (0.66, 0.53, 0.36)       # lower tube, grooves
SPICULE = (0.97, 0.95, 0.86)     # glassy rib highlights and needles
VENT = (0.20, 0.15, 0.10)        # inside
HOLD = (0.52, 0.45, 0.34)


def axis(t):
    """Centre line: a gentle curve, upright at the base."""
    return Vector((BEND * t * t, 0.35 * BEND * t ** 3, HEIGHT * t))


def radius(t):
    return R_BASE + (R_TOP - R_BASE) * t ** 0.9 - 0.012 * nh.smoothstep(0.0, 0.06, 0.06 - t)


def frame(t):
    fwd = (axis(min(1.0, t + 0.01)) - axis(max(0.0, t - 0.01))).normalized()
    side = fwd.cross(Vector((0, 1, 0))).normalized()
    return side, side.cross(fwd).normalized()


def rib(a):
    """Longitudinal ribs: sharp raised bundles of oxeas with shallow grooves between them."""
    return math.cos(a * RIBS) ** 8


def tube():
    bm = bmesh.new()
    rings = []
    for i in range(RINGS + 1):
        t = i / RINGS
        c, (s, u) = axis(t), frame(t)
        r = radius(t)
        ring = []
        for k in range(SIDES):
            a = k / SIDES * math.tau + 0.3 * t   # ribs spiral very slightly
            rr = r * (1.0 + RIB_DEPTH * (rib(a) - 0.4))
            ring.append(bm.verts.new(c + s * math.cos(a) * rr + u * math.sin(a) * rr))
        rings.append(ring)
    # lip and inner wall back down the spongocoel
    n_in = max(3, round(INNER_DEPTH * RINGS))
    for i in range(RINGS, RINGS - n_in - 1, -1):
        t = i / RINGS
        c, (s, u) = axis(t), frame(t)
        r = max(0.01, radius(t) - WALL)
        rings.append([bm.verts.new(c + s * math.cos(k / SIDES * math.tau + 0.3 * t) * r
                                   + u * math.sin(k / SIDES * math.tau + 0.3 * t) * r) for k in range(SIDES)])
    for a, b in zip(rings, rings[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def local(co):
    """(t along the tube, angle around it, radial distance) for a point on the tube."""
    t = max(0.0, min(1.0, co.z / HEIGHT))
    c, (s, u) = axis(t), frame(t)
    d = co - c
    return t, math.atan2(d.dot(u), d.dot(s)) - 0.3 * t, d.length


def build():
    rng = random.Random(SEED)
    warp = Vector((rng.random() * 30, rng.random() * 30, rng.random() * 30))
    mb = nh.MeshBuilder()

    def body_col(co, n):
        t, a, d = local(co)
        if d < radius(t) - WALL * 0.5:  # inner wall
            return nh.lerp(VENT, SHADE, 0.4 * nh.smoothstep(0.97, 1.0, t))
        c = nh.lerp(SHADE, STRAW, nh.smoothstep(0.0, 0.45, t))
        c = nh.lerp(c, SHADE, 0.2 * nh.smoothstep(0.2, -0.4, noise.noise(co * 5 + warp)))
        c = nh.lerp(c, SPICULE, 0.65 * rib(a))                                  # oxea bundles
        c = nh.lerp(c, SHADE, 0.18 * (1 - rib(a)) * math.cos(t * HEIGHT * 140) ** 8)  # fine transverse spicules
        return nh.lerp(c, SPICULE, 0.6 * nh.smoothstep(0.985, 1.0, t))            # pale lip

    mb.add(tube(), body_col)

    # small rounded holdfast
    mb.add(nh.ellipsoid((0, 0, 0.01), (0.085, 0.08, 0.035), subdivisions=2,
                        deform=lambda n: 1.0 + 0.1 * noise.noise(n * 2.5 + warp)), HOLD)

    # plumose fringe: thin needles flaring up and out from the rim
    c0, (s, u) = axis(1.0), frame(1.0)
    fwd = (axis(1.0) - axis(0.98)).normalized()
    for k in range(NEEDLES):
        a = (k + rng.uniform(-0.3, 0.3)) / NEEDLES * math.tau
        radial = s * math.cos(a) + u * math.sin(a)
        r = radius(1.0) - WALL * 0.5
        base = c0 + radial * r - fwd * 0.03
        length = rng.uniform(0.09, 0.16)
        flare = rng.uniform(0.25, 0.55)
        mid = base + (fwd + radial * flare * 0.5).normalized() * length * 0.5
        tip = base + (fwd + radial * flare).normalized() * length
        mb.add(nh.tube([base, mid, tip], [0.006, 0.004, 0.0], sides=5, cap_start=True),
               lambda co, n, b=base, l=length: nh.lerp(STRAW, SPICULE, min(1.0, (co - b).length / l + 0.3)))

    nv.mud_patch(mb, rng, 0.22, 0.42, count=7, size=(0.035, 0.07))
    obj = mb.to_object("LeptomitusZitteli", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "LeptomitusZitteli", ground=(0.40, 0.38, 0.34), views=((20, 15), (110, 25), (10, 65)))
