"""
Shared builder for the Hazelia models (hazelia_palmata.py, hazelia_crateria.py): Middle
Cambrian Burgess Shale demosponges (Hazeliidae) with a thin wall of tightly packed monaxon
spicules in mainly radial, anastomosing tracts, a fine net of spicules in the skin and a small
basal attachment.

The body is a thin-walled cup: a closed parametric shell (outer wall from the base up to a
rounded lip, then the inner wall back down into the cavity, closed by a floor) like
nh_protospongia's sacs, but:
  * the cross-section can be squashed (sx, sy) and the cup curled sideways (curl), so a
    flattened cup reads as a cupped hand;
  * the rim height varies around the margin (lobes), giving a lobed / palmate margin;
  * radial spicule tracts run from the base up to the margin as low ribs and pale stripes,
    wandering a little so they look anastomosing, and (optionally) project past the margin
    as fine needles; short bristles stud the outer wall.

A species script fills a HazeliaSpec and calls build(spec, "ModelName").
Fixed style: pivot at the base (z = 0).
"""

import math
import random
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_protospongia as npr   # Profile (smooth arc-length (r, z) curve)
import nh_vauxia as nv          # mud_patch


@dataclass
class HazeliaSpec:
    seed: int = 1
    profile: list = field(default_factory=lambda: [(0.05, 0.0), (0.3, 0.3), (0.5, 0.8)])
    sx: float = 1.0                # cross-section scale along X
    sy: float = 1.0                # ... along Y (front-back)
    curl: float = 0.0              # sideways (Y) bend of the cup with height (cupped hand)
    segs: int = 60                 # vertices around
    rows: int = 22                 # outer wall rows
    inner_rows: int = 7
    lip_rings: int = 3
    wall: float = 0.04
    inner_bottom: float = 0.35     # profile fraction where the visible inner wall ends
    lobes: int = 0                 # number of marginal lobes
    lobe_depth: float = 0.0        # notch depth between lobes (profile fraction)
    lobe_sharp: float = 0.5        # <1 = broad lobes with narrow notches
    lobe_flare: float = 0.0        # extra outward lean of the lobe tips
    lobe_across: bool = False      # lay the lobes out across the width (X) instead of around,
                                   # so front and back walls share them (flattened fan / hand)
    rough: float = 0.0             # small-scale lumpiness of the wall
    pores: tuple = (0.0, 0.0)      # (frequency, strength) of dark canal openings painted on the wall
    wobble: float = 0.05           # irregular bulging of the wall
    tracts: int = 20               # radial spicule tracts
    tract_relief: float = 0.012
    tract_wander: float = 0.25     # sideways wander of the tracts (fraction of the spacing)
    needles: tuple = (0, (0.05, 0.1))     # (per-tract needles past the margin, length range)
    bristles: tuple = (0, (0.02, 0.04))   # (count of short bristles on the wall, length range)
    holdfast: tuple = (0.09, 0.035)        # (radius, height) of the basal attachment
    mud: tuple = (0.35, 0.6)
    body: tuple = (0.80, 0.70, 0.52)
    shade: tuple = (0.58, 0.48, 0.34)
    tract: tuple = (0.93, 0.87, 0.72)
    rim: tuple = (0.92, 0.86, 0.70)
    inside: tuple = (0.30, 0.23, 0.16)
    spicule: tuple = (0.96, 0.94, 0.86)
    hold_col: tuple = (0.48, 0.40, 0.30)


def build(spec, name):
    rng = random.Random(spec.seed)
    prof = npr.Profile(spec.profile)
    n = spec.segs
    warp = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))
    zmax = max(p[1] for p in spec.profile)

    # per-lobe amplitudes so the margin isn't perfectly regular
    amps = [rng.uniform(0.35, 1.0) for _ in range(max(1, spec.lobes))]
    phase = rng.uniform(0, math.tau)

    def lobe(theta):
        """1 at a lobe tip, 0 in a notch."""
        if not spec.lobes:
            return 1.0
        if spec.lobe_across:
            x = (math.cos(theta) + 1.0) * 0.5 * spec.lobes
            i = min(int(x), spec.lobes - 1)
            bump = math.sin(min(1.0, x - i) * math.pi) ** spec.lobe_sharp
            return bump * amps[i] + (1 - amps[i]) * 0.3 * bump
        x = (theta + phase) / math.tau * spec.lobes
        i = int(math.floor(x)) % spec.lobes
        f = x - math.floor(x)
        bump = math.sin(f * math.pi) ** spec.lobe_sharp
        return bump * amps[i] + (1 - amps[i]) * 0.3 * bump

    def s_end(theta):
        return 1.0 - spec.lobe_depth * (1.0 - lobe(theta))

    def tract_u(theta, s):
        """Tract coordinate around (integer = on a tract), wandering with height."""
        w = spec.tract_wander * noise.noise(Vector((math.cos(theta) * 1.5, math.sin(theta) * 1.5, s * 3.0)) + warp)
        return theta / math.tau * spec.tracts + w

    def tract_w(theta, s):
        u = tract_u(theta, s)
        d = abs(u - round(u))
        return nh.smoothstep(0.32, 0.0, d)

    def bulge(theta, z):
        p = Vector((math.cos(theta) * 1.2, math.sin(theta) * 1.2, z * 2.0)) + warp
        return 1.0 + spec.wobble * noise.noise(p)

    def place(theta, s, normal_off=0.0, tangent_off=0.0, extra=0.0):
        (r, z), (nr, nz) = prof.at(s)
        tr, tz = -nz, nr
        lean = spec.lobe_flare * nh.smoothstep(0.6, 1.0, s) * lobe(theta)
        c, sn = math.cos(theta), math.sin(theta)
        lump = spec.rough * noise.noise(Vector((c * 5, sn * 5, z * 9)) + warp * 1.7) if spec.rough else 0.0
        rad = r * bulge(theta, z) + tr * tangent_off + lean * s
        zz = z + tz * tangent_off
        # offsets along the wall normal are applied after the cross-section squash, so the wall
        # keeps its thickness on a flattened cup
        ex, ey = c * spec.sy, sn * spec.sx
        el = math.hypot(ex, ey) or 1.0
        off = normal_off + extra + lump
        x = c * rad * spec.sx + ex / el * nr * off
        y = sn * rad * spec.sy + ey / el * nr * off
        zz += nz * off
        y += spec.curl * (zz / zmax) ** 2
        return Vector((x, y, zz))

    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}
    thetas = [k / n * math.tau for k in range(n)]
    if spec.lobe_across:
        # space the vertices evenly across the width so the middle lobes get as many as the
        # outer ones (blended with even angles to keep the side edges round)
        def even_x(t):
            return 0.7 * math.acos(1.0 - 2.0 * t) + 0.3 * math.pi * t
        half = n // 2
        thetas = [even_x(k / half) for k in range(half)] + \
                 [math.tau - even_x(1.0 - k / (n - half)) for k in range(n - half)]

    def outer_col(theta, s, z):
        c = nh.lerp(spec.shade, spec.body, nh.smoothstep(0.0, 0.45, s))
        c = nh.lerp(c, spec.shade, 0.25 * nh.smoothstep(0.1, -0.4, noise.noise(Vector((theta * 2, s * 6, 0)) + warp)))
        c = nh.lerp(c, spec.tract, 0.75 * tract_w(theta, s) * nh.smoothstep(0.05, 0.25, s))
        if spec.pores[1]:
            p = Vector((math.cos(theta) * 0.6, math.sin(theta) * 0.6, z * 0.6 / zmax * 1.2)) * spec.pores[0]
            d = noise.voronoi(p + warp)[0][0]
            c = nh.lerp(c, spec.shade, spec.pores[1] * nh.smoothstep(0.28, 0.1, d) * nh.smoothstep(0.1, 0.3, s))
        c = nh.lerp(c, spec.rim, 0.6 * nh.smoothstep(0.92, 1.0, s / s_end(theta)))
        k = 0.92 + 0.12 * noise.noise(Vector((theta * 6, s * 30, 1.0)) + warp)
        return tuple(min(1.0, x * k) for x in c)

    rings = []
    for i in range(spec.rows + 1):
        t = i / spec.rows
        ring = []
        for th in thetas:
            s = t * s_end(th)
            h = spec.tract_relief * tract_w(th, s) * nh.smoothstep(0.05, 0.25, s) * (1 - 0.6 * t ** 8)
            v = bm.verts.new(place(th, s, extra=h))
            vcol[v] = outer_col(th, s, v.co.z)
            ring.append(v)
        rings.append(ring)
    for i in range(1, spec.lip_rings + 1):
        a = i / (spec.lip_rings + 1) * math.pi
        off_n = spec.wall * 0.5 * (math.cos(a) - 1.0)
        off_t = spec.wall * 0.5 * math.sin(a)
        ring = []
        for th in thetas:
            v = bm.verts.new(place(th, s_end(th), off_n, off_t))
            vcol[v] = spec.rim
            ring.append(v)
        rings.append(ring)
    for i in range(spec.inner_rows + 1):
        f = (i / spec.inner_rows) ** 1.3
        ring = []
        for th in thetas:
            se = s_end(th)
            s = se - (se - spec.inner_bottom) * f
            v = bm.verts.new(place(th, s, -spec.wall))
            vcol[v] = nh.lerp(spec.rim, spec.inside, nh.smoothstep(0.0, 0.12, se - s))
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    cb = bm.verts.new(sum((v.co for v in rings[0]), Vector()) / n - Vector((0, 0, 0.005)))
    vcol[cb] = spec.shade
    for k in range(n):
        bm.faces.new([rings[0][(k + 1) % n], rings[0][k], cb])
    last = rings[-1]
    ci = bm.verts.new(sum((v.co for v in last), Vector()) / n - Vector((0, 0, 0.01)))
    vcol[ci] = spec.inside
    for k in range(n):
        bm.faces.new([last[k], last[(k + 1) % n], ci])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
        for loop in f.loops:
            c = vcol[loop.vert]
            loop[col] = (c[0], c[1], c[2], 1.0)

    mb = nh.MeshBuilder()
    mb.add(bm)

    def needle(base, direction, length, r0):
        tip = base + direction * length
        mb.add(nh.tube([base, tip], [r0, 0.0], sides=3, cap_start=True),
               lambda co, nrm, b=base: nh.lerp(spec.tract, spec.spicule, min(1.0, (co - b).length / length + 0.2)))

    # tracts projecting past the margin
    count, (l0, l1) = spec.needles
    for j in range(spec.tracts):
        for _ in range(count):
            # find the angle of tract j at the rim
            th = (j + rng.uniform(-0.15, 0.15)) / spec.tracts * math.tau
            se = s_end(th)
            base = place(th, se - 0.01, -spec.wall * 0.5)
            up = place(th, se, -spec.wall * 0.5) - place(th, se - 0.03, -spec.wall * 0.5)
            d = (up.normalized() + Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(-0.1, 0.1)))).normalized()
            needle(base - d * 0.01, d, rng.uniform(l0, l1), 0.006)

    # short bristles on the outer wall, mostly along the tracts
    count, (l0, l1) = spec.bristles
    for _ in range(count):
        j = rng.randrange(spec.tracts)
        th = (j + rng.uniform(-0.2, 0.2)) / spec.tracts * math.tau
        s = s_end(th) * rng.uniform(0.25, 0.95)
        p = place(th, s)
        q = place(th, s, 0.01)
        out = (q - p).normalized()
        up = (place(th, min(1.0, s + 0.02)) - p).normalized()
        d = (out * 0.6 + up * 0.8).normalized()
        needle(p - d * 0.004, d, rng.uniform(l0, l1), 0.0045)

    hr, hh = spec.holdfast
    if hr:
        mb.add(nh.ellipsoid((0, 0, hh * 0.3), (hr, hr * 0.9, hh), subdivisions=2,
                            deform=lambda nn: 1.0 + 0.12 * noise.noise(nn * 2.5 + warp)), spec.hold_col)
    if spec.mud:
        nv.mud_patch(mb, rng, *spec.mud)
    obj = mb.to_object(name, roughness=0.75)
    nh.ground_to_zero(obj)
    return obj
