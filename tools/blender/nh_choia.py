"""
Shared builder for the Choia models (choia_carteri.py, choia_hindei.py): Cambrian
"protomonaxonid" demosponges, a low conical disc made of a radiating thatch of fine
monaxon spicules, ringed by long, stouter coronal spicules that splay out past the margin.

The sponge was not anchored: it sat loose on the mud, the coronal spicules fanned out
around it like a starburst and propping the disc a little above the sea floor. Here the
lower tier of coronal spicules rests on the ground (their tips set the z = 0 pivot) and
an upper tier rises up and outward from the top of the margin.

Each part:
  * disc: a lathed, rotationally symmetric low cone / dome with a rounded rim and a
    slightly concave underside, with radial ribs (relief and colour stripes) for the
    spicule thatch and a small osculum dimple at the apex;
  * coronal spicules: tapering 5-sided tubes rooted inside the disc so they appear to
    grow out of it, gently curved, pale and glassy (siliceous), darker near the base.

A species script fills a ChoiaSpec and calls build(spec, "ModelName").
"""

import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Vector, noise

import nh_model as nh


@dataclass
class ChoiaSpec:
    seed: int = 1
    disc_r: float = 0.4          # disc radius
    disc_h: float = 0.26         # apex height above the underside
    rim_t: float = 0.07          # rim thickness
    cone_p: float = 1.3          # top profile exponent (1 = straight cone, >1 = domed)
    lift: float = 0.06           # underside height above the ground
    segments: int = 80           # lathe segments around the disc
    ribs: int = 40               # radial ribs (spicule tracts) on the disc
    rib_depth: float = 0.006     # rib relief height
    osculum_r: float = 0.05      # apex osculum radius
    # coronal spicules: (count, length range, base radius range, elevation range in degrees)
    upper: tuple = (34, (0.45, 0.65), (0.011, 0.014), (14.0, 36.0))
    lower: tuple = (30, (0.50, 0.68), (0.012, 0.015), (None, None))   # None: rest the tip on the ground
    jitter: float = 0.12         # random spread of the spicule azimuths (fraction of the spacing)
    sag: float = 0.05            # downward curve of the spicules (fraction of their length)
    body: tuple = (0.86, 0.78, 0.60)
    body_dark: tuple = (0.62, 0.52, 0.36)
    rib_col: tuple = (0.94, 0.88, 0.72)
    osculum: tuple = (0.28, 0.20, 0.13)
    spicule_base: tuple = (0.80, 0.74, 0.60)
    spicule_tip: tuple = (0.96, 0.95, 0.90)
    max_disc_tris: int = 0       # 0 = keep the lathe resolution


def _top_z(spec, u):
    """Height of the upper surface at radial fraction u (0 = apex, 1 = rim top)."""
    h_top = spec.disc_h - spec.rim_t
    return spec.lift + spec.rim_t + h_top * (1.0 - u ** spec.cone_p)


def _profile(spec):
    """(r, z) points from the apex, down the upper surface, round the rim, back along the
    underside to the centre."""
    pts = []
    n_top = 9
    for i in range(n_top + 1):
        u = i / n_top
        u = u ** 0.85
        pts.append((spec.disc_r * u, _top_z(spec, u)))
    # rounded rim: half circle from top of the rim to its bottom
    rc = spec.rim_t * 0.5
    zc = spec.lift + rc
    for k in range(1, 4):
        a = math.pi * 0.5 - k / 4 * math.pi
        pts.append((spec.disc_r + rc * 0.9 * math.cos(a), zc + rc * math.sin(a)))
    # underside: slightly concave, rising toward the centre
    n_bot = 3
    for i in range(n_bot, -1, -1):
        u = i / n_bot
        pts.append((spec.disc_r * u, spec.lift + 0.25 * spec.rim_t * (1 - u * u)))
    return pts


def _rib(spec, a):
    return 0.5 + 0.5 * math.cos(a * spec.ribs)


def disc(spec):
    bm = bmesh.new()
    prof = _profile(spec)
    n = spec.segments
    rings = []
    seed = Vector((spec.seed * 3.1, 1.7, 0.4))
    for r, z in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        u = r / spec.disc_r
        ring = []
        for j in range(n):
            a = j / n * math.tau
            # rib relief on the upper surface, fading at the apex and the rim
            top = z > spec.lift + spec.rim_t * 0.6
            k = spec.rib_depth * _rib(spec, a) * nh.smoothstep(0.15, 0.45, u) if top else 0.0
            k += 0.008 * noise.noise(Vector((math.cos(a) * 2.5, math.sin(a) * 2.5, z * 4)) + seed)
            # osculum dimple at the apex
            dz = -0.03 * nh.smoothstep(spec.osculum_r * 1.4, spec.osculum_r * 0.4, r) if top else 0.0
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z + k + dz)))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        if len(ra) == 1:
            for j in range(n):
                bm.faces.new([ra[0], rb[j], rb[(j + 1) % n]])
        elif len(rb) == 1:
            for j in range(n):
                bm.faces.new([ra[j], ra[(j + 1) % n], rb[0]])
        else:
            for j in range(n):
                k = (j + 1) % n
                bm.faces.new([ra[j], ra[k], rb[k], rb[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, nrm):
        r = math.hypot(co.x, co.y)
        u = r / spec.disc_r
        a = math.atan2(co.y, co.x)
        if r < spec.osculum_r * 0.8 and nrm.z > 0:
            return spec.osculum
        c = nh.lerp(spec.body_dark, spec.body, nh.smoothstep(-0.2, 0.6, nrm.z))
        c = nh.lerp(c, spec.rib_col, 0.75 * _rib(spec, a) ** 3 * nh.smoothstep(0.1, 0.4, u) * (nrm.z > 0))
        c = nh.lerp(c, spec.body_dark, 0.5 * nh.smoothstep(spec.osculum_r * 2.2, spec.osculum_r, r))
        t = 0.9 + 0.2 * noise.noise(co * 14 + Vector((spec.seed, 0, 0)))
        return tuple(min(1.0, x * t) for x in c)
    return bm, color


def spicule(spec, rng, a, length, r0, elev):
    """One coronal spicule at azimuth a. elev: degrees above horizontal, or None to droop the
    tip to the ground."""
    out = Vector((math.cos(a), math.sin(a), 0.0))
    # rooted just inside the margin so each spicule emerges cleanly from the rim
    root_r = spec.disc_r * rng.uniform(0.86, 0.92)
    root_z = spec.lift + spec.rim_t * (0.7 if elev is not None else 0.3)
    root = out * root_r + Vector((0, 0, root_z))
    if elev is None:
        # from the rim down to a tip resting on the ground
        tip = out * (spec.disc_r + length) + Vector((0, 0, rng.uniform(0.0, 0.01)))
    else:
        e = math.radians(elev)
        tip = root + (out * math.cos(e) + Vector((0, 0, math.sin(e)))) * (length + spec.disc_r - root_r)
    # slight sideways bend so the fan doesn't look ruled
    side = Vector((-out.y, out.x, 0.0)) * rng.uniform(-0.04, 0.04) * length
    pts, radii = [], []
    steps = 4
    for k in range(steps + 1):
        t = k / steps
        p = root.lerp(tip, t) + side * math.sin(t * math.pi)
        p.z -= spec.sag * length * math.sin(t * math.pi) * (1.0 if elev is not None else 0.4)
        pts.append(p)
        radii.append(r0 * (1.0 - 0.75 * t ** 1.2))
    radii[-1] = 0.0
    bm = nh.tube(pts, radii, sides=5, cap_start=False)
    rim = spec.disc_r - root_r
    total = (tip - root).length

    def color(co, nrm):
        t = nh.smoothstep(rim / total, 1.0, (co - root).length / total)
        return nh.lerp(spec.spicule_base, spec.spicule_tip, t ** 0.7)
    return bm, color


def build(spec, name):
    rng = random.Random(spec.seed)
    mb = nh.MeshBuilder()
    mb.add(*disc(spec))
    for tier_i, (count, (l0, l1), (r0, r1), (e0, e1)) in enumerate((spec.upper, spec.lower)):
        offset = rng.random() * math.tau
        for k in range(count):
            a = offset + (k + rng.uniform(-spec.jitter, spec.jitter)) / count * math.tau
            elev = None if e0 is None else rng.uniform(e0, e1)
            mb.add(*spicule(spec, rng, a, rng.uniform(l0, l1), rng.uniform(r0, r1), elev))
    obj = mb.to_object(name, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj
