"""
Procedural speckled rattlesnake (Crotalus mitchellii) for map colonies (large-animal detail).

A heavy body in a loose two-tier coil on the ground, the front third rising in an
S-curve with the broad triangular head poised over the coil, and the rattle raised
up from the outside of the coil. The body is one lofted tube (no fusing needed), so
the scale pattern and colours can be laid out along the body: keeled diamond scales
displaced into the surface, broad belly plates, irregular speckled crossbands on a
sandy pink-tan to pale-grey ground, and the dark-and-pale banded tail before the
rattle. The head is part of the same loft (wide jaws, narrow snout, flat crown).
Crisp details: rattle buttons, eyes with vertical pupils under raised supraocular
scales, heat pits, nostrils and a flicking forked tongue.
Faces -Y (the head looks forward), pivot on the ground.

Usage:
  blender --background --python tools/blender/crotalus_mitchellii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SpeckledRattlesnake.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

SAND = (0.80, 0.65, 0.53)      # pinkish-tan ground colour
GREY = (0.72, 0.69, 0.64)      # pale grey ground colour
BAND = (0.45, 0.33, 0.28)      # crossbands
SPECK_DARK = (0.24, 0.17, 0.14)
SPECK_LIGHT = (0.95, 0.90, 0.82)
BELLY = (0.90, 0.84, 0.72)
TAIL_DARK = (0.17, 0.14, 0.13)
TAIL_PALE = (0.74, 0.71, 0.66)
HEAD = (0.82, 0.71, 0.60)
LIP = (0.92, 0.87, 0.78)
RATTLE = (0.82, 0.72, 0.55)
RATTLE_GROOVE = (0.50, 0.41, 0.30)
EYE = (0.72, 0.56, 0.32)
PUPIL = (0.02, 0.02, 0.02)
PIT = (0.10, 0.07, 0.06)
TONGUE = (0.10, 0.05, 0.06)

SIDES = 26          # vertices around the body
RINGS = 285         # rings along the body
BODY_R = 0.046      # radius of the thick mid-body
HEAD_LEN = 0.112


# ---------------------------------------------------------------- centre line

def catmull_rom(pts, samples_per_seg=12):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(samples_per_seg):
            t = k / samples_per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def resample(pts, n, head_rings=0, head_span=0.0):
    """n points spaced by arc length (the last head_span packed with head_rings of them,
    so the small head gets enough vertices); returns (points, arc lengths, total length)."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + (b - a).length)
    total = d[-1]
    nb = n - head_rings
    split = total - head_span
    ells = [split * i / (nb - 1) for i in range(nb)] if head_rings else [total * i / (n - 1) for i in range(n)]
    ells += [split + head_span * (i + 1) / head_rings for i in range(head_rings)]
    out, j = [], 0
    for s in ells:
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        seg = d[j + 1] - d[j] or 1.0
        out.append(pts[j].lerp(pts[j + 1], (s - d[j]) / seg))
    return out, ells, total


def centre_line():
    """Tail (rattle end) -> lower coil -> upper coil -> rising S-curve -> snout."""
    r1, r2 = 0.215, 0.14            # lower / upper coil radius
    z1, z2 = BODY_R, BODY_R + 0.074  # upper tier rests in the groove of the lower one
    turns = 1.85
    th_end = math.pi / 2 + 2 * math.pi
    th0 = th_end - turns * 2 * math.pi

    spiral = []
    steps = 40
    for i in range(steps + 1):
        s = i / steps
        th = th0 + s * turns * 2 * math.pi
        k = nh.smoothstep(0.42, 0.64, s)
        r = r1 + (r2 - r1) * k
        z = z1 + (z2 - z1) * k
        spiral.append(Vector((math.cos(th) * r, math.sin(th) * r, z)))

    q0 = spiral[0]
    radial = Vector((q0.x, q0.y, 0)).normalized()
    tan0 = Vector((-math.sin(th0), math.cos(th0), 0))
    t2 = q0 - tan0 * 0.06 + radial * 0.025 + Vector((0, 0, 0.07))
    t3 = t2 - tan0 * 0.005 + radial * 0.004 + Vector((0, 0, 0.13))   # rattle base, pointing up

    rise = [Vector(p) for p in (
        (-0.07, 0.07, 0.16),
        (-0.03, -0.01, 0.23),
        (0.035, 0.03, 0.30),     # the S bends back
        (0.01, -0.035, 0.345),
        (0.0, -0.10, 0.335),     # head base
        (0.0, -0.10 - HEAD_LEN, 0.312),  # snout tip
    )]
    # mirrored so the raised rattle stands on the right, clear of the rising neck
    return [Vector((-p.x, p.y, p.z)) for p in [t3, t2] + spiral + rise]


# ---------------------------------------------------------------- body profile

def head_shape(u):
    """Width / height multipliers of the head along u (0 = neck, 1 = snout)."""
    # from above: a broad, flat triangle - narrow neck, swollen venom glands at the back
    # of the jaws, straight sides tapering to a blunt snout
    if u < 0.22:
        k = nh.smoothstep(0.0, 0.22, u)
        w = 0.019 + (0.066 - 0.019) * k
        h = 0.019 + (0.021 - 0.019) * k
    elif u < 0.88:
        k = (u - 0.22) / 0.66
        w = 0.066 + (0.024 - 0.066) * k
        h = 0.021 + (0.016 - 0.021) * k
    else:
        k = (u - 0.88) / 0.12
        c = math.sqrt(max(0.0, 1.0 - k * k))
        w, h = 0.024 * c, 0.016 * c
    return w, h


def profile(ell, total):
    """(width, height, head u or None) of the cross-section at arc length ell."""
    head_start = total - HEAD_LEN
    if ell >= head_start:
        u = (ell - head_start) / HEAD_LEN
        w, h = head_shape(u)
        return w, h, u
    s = ell / total
    r = 0.013 + (BODY_R - 0.013) * nh.smoothstep(0.0, 0.27, s)
    r += (0.019 - r) * nh.smoothstep(total - 0.5, head_start, ell) ** 0.8
    return r, r, None


# ---------------------------------------------------------------- paint

def _hash(i, k, salt=0):
    """Deterministic per-vertex random number in [0, 1) - fine pepper at vertex resolution."""
    h = (i * 73856093) ^ (k * 19349663) ^ (salt * 83492791)
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def pepper(c, i, k, dark=0.14, light=0.1):
    r = _hash(i, k)
    if r < dark:
        return nh.lerp(c, SPECK_DARK, 0.4 + 0.25 * _hash(i, k, 1))
    if r > 1.0 - light:
        return nh.lerp(c, SPECK_LIGHT, 0.4 + 0.25 * _hash(i, k, 2))
    return c


def body_colour(co, ell, total, a, u, i=0, k=0):
    up = math.sin(a)
    lat = abs(math.cos(a))
    slow = 0.5 + 0.5 * noise.noise(Vector((ell * 3.0, 0.0, 1.3)))
    c = nh.lerp(SAND, GREY, slow)

    if u is not None:                                   # head
        c = nh.lerp(nh.lerp(HEAD, SAND, 0.6), GREY, 0.3 * slow)
        if up < -0.5:
            return LIP
        if -0.5 <= up < -0.2 and u > 0.12:             # row of pale lip scales with dark seams
            seam = ((ell / 0.0085) % 1.0) < 0.25
            return nh.lerp(LIP, SPECK_DARK, 0.5) if seam or up > -0.25 else LIP
        # dark post-ocular stripe: from the eye back and down to the corner of the jaw
        line = -0.15 + (u - 0.1) / 0.5 * 0.5
        if 0.04 < u < 0.62 and lat > 0.3 and abs(up - line) < 0.14:
            return pepper(BAND, i, k, 0.05, 0.03)
        return pepper(c, i, k, 0.05, 0.03)

    tail_end = 0.13 * total
    if ell < tail_end:                                  # bold black and pale rings before the rattle
        ph = (ell / 0.03) % 1.0
        return TAIL_DARK if ph < 0.52 else TAIL_PALE

    if up < -0.6:                                       # belly plates with faint seams
        seam = abs(((ell / 0.016) % 1.0) - 0.5) > 0.42
        return pepper(nh.lerp(BELLY, SAND, 0.35 if seam else 0.0), i, k, 0.06, 0.0)

    # crisp, regularly spaced crossbands: widest along the spine (hourglass / diamond-ish),
    # narrowing down the flanks, edges slightly ragged
    period = 0.12
    ph = (ell - 0.04) / period + 0.04 * noise.noise(Vector((ell * 4.0, 0.0, 4.0)))
    d = abs((ph % 1.0) - 0.5) * period                 # distance to the band centre (units)
    dorsal = max(0.0, up)
    half = 0.012 + 0.022 * dorsal ** 1.2
    half *= 1.0 + 0.08 * noise.noise(Vector((ell * 12.0, a * 1.5, 7.0)))
    if up < -0.35:
        half *= max(0.0, (up + 0.6) / 0.25)
    if d < half:
        return pepper(BAND, i, k, 0.1, 0.12)
    if d < half + 0.008:                               # pale band edging
        return pepper(nh.lerp(c, SPECK_LIGHT, 0.5), i, k, 0.08, 0.0)
    return pepper(c, i, k, 0.14, 0.08)


def scale_bump(ell, a, u):
    """Keeled, overlapping diamond scales on the back and flanks; flat belly plates."""
    if u is not None:
        return 0.0008 * noise.noise(Vector((ell * 300.0, a * 6.0, 0.0)))
    up = math.sin(a)
    if up < -0.6:
        return 0.0
    lam = 0.034
    rows = 6.5
    p = ell / lam
    q = a * rows / (2 * math.pi)
    f = math.cos(2 * math.pi * (p + q)) * math.cos(2 * math.pi * (p - q))
    return 0.0032 * max(0.0, f)


# ---------------------------------------------------------------- loft

def loft():
    pts, ells, total = resample(catmull_rom(centre_line(), 14), RINGS, head_rings=40, head_span=HEAD_LEN + 0.04)
    frames = []
    prev_side = None
    for i, c in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        up_ref = Vector((0, 0, 1))
        side = t.cross(up_ref)
        if side.length < 0.25 and prev_side is not None:
            side = prev_side - t * prev_side.dot(t)
        side.normalize()
        if prev_side is not None and side.dot(prev_side) < 0:
            side = -side
        prev_side = side
        up = side.cross(t).normalized()
        if up.z < 0 and abs(t.z) < 0.9:
            up, side = -up, -side
        frames.append((c, t, side, up))

    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    rings, vcol = [], {}
    head_frames = []
    for i, (c, t, side, up) in enumerate(frames):
        ell = ells[i]
        w, h, u = profile(ell, total)
        if u is not None:
            head_frames.append((u, c, t, side, up, w, h))
        if i == RINGS - 1:
            v = bm.verts.new(c)
            vcol[v] = body_colour(c, ell, total, -math.pi / 2 + 0.01, u, i, 0)
            rings.append([v])
            continue
        ring = []
        for k in range(SIDES):
            a = k / SIDES * math.tau
            ca, sa = math.cos(a), math.sin(a)
            hh = h * (0.82 if sa < 0 else 1.0)           # flatter belly
            if u is not None:                             # spade head: flat crown, flat jaw
                ca = math.copysign(abs(ca) ** 0.55, ca)
                sa = math.copysign(abs(sa) ** 0.7, sa)
                hh = h * (0.7 if sa < 0 else 1.0)
            p = c + side * ca * w + up * sa * hh
            n = (side * ca + up * sa).normalized()
            p += n * scale_bump(ell, a, u)
            v = bm.verts.new(p)
            vcol[v] = body_colour(p, ell, total, a, u, i, k)
            ring.append(v)
        rings.append(ring)

    for a_r, b_r in zip(rings, rings[1:]):
        if len(b_r) == 1:
            for k in range(SIDES):
                bm.faces.new([a_r[k], a_r[(k + 1) % SIDES], b_r[0]])
        else:
            for k in range(SIDES):
                j = (k + 1) % SIDES
                bm.faces.new([a_r[k], a_r[j], b_r[j], b_r[k]])
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for l in f.loops:
            c = vcol[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    tail_dir = (frames[0][0] - frames[3][0]).normalized()
    return bm, frames[0][0], tail_dir, head_frames


# ---------------------------------------------------------------- crisp details

def oriented_ellipsoid(center, axes, radii, segments=12, rings=8):
    """UV ellipsoid with radii along the given (x, y, z) axis vectors."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
    m = Matrix((axes[0], axes[1], axes[2])).transposed().to_4x4()
    nh.transform(bm, m)
    nh.transform(bm, Matrix.Translation(center))
    return bm


def head_point(head_frames, u, lat, vert):
    """Point on the head at u (0 neck .. 1 snout), lat/vert as fractions of width/height."""
    best = min(head_frames, key=lambda f: abs(f[0] - u))
    _u, c, t, side, up, w, h = best
    return c + side * w * lat + up * h * vert, t, side, up, w, h


def rattle(base, direction):
    out = []
    d = direction.normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 0.2:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d).normalized()
    pos = base.copy()
    for k in range(7):
        s = 1.28 * (1.0 - 0.06 * k)
        length = 0.016 * s
        pos = pos + d * (length * (0.45 if k else 0.3))

        def colour(co, n, c=pos.copy(), L=length):
            along = (co - c).dot(d) / L
            if along < -0.55:
                return RATTLE_GROOVE
            return nh.lerp(RATTLE, (0.92, 0.85, 0.7), max(0.0, along) * 0.6)

        out.append((oriented_ellipsoid(pos, (side, d, up), (0.019 * s, length, 0.0105 * s), 12, 8), colour))
        # the middle lobe of each button bulges on both faces
        for sy in (1, -1):
            out.append((oriented_ellipsoid(pos + up * sy * 0.006 * s, (side, d, up),
                                           (0.0085 * s, length * 0.85, 0.0065 * s), 8, 6), colour))
        pos = pos + d * length * 0.45
    return out


def details(head_frames, tail_tip, tail_dir):
    out = rattle(tail_tip - tail_dir * 0.006, tail_dir)
    for sx in (1, -1):
        # eye bulging from the side of the head, with a vertical slit pupil
        p, t, side, up, w, h = head_point(head_frames, 0.6, sx * 0.84, 0.42)
        s = side * sx
        out.append((nh.ellipsoid(p, (0.0078, 0.0078, 0.0078), subdivisions=2), EYE))
        out.append((oriented_ellipsoid(p + s * 0.007, (s, t, up), (0.0014, 0.0016, 0.0058), 8, 6), PUPIL))
        # raised supraocular scale overhanging the eye
        q, *_ = head_point(head_frames, 0.6, sx * 0.72, 0.9)
        out.append((oriented_ellipsoid(q + s * 0.002 - up * 0.0006, (s, t, up), (0.0072, 0.0115, 0.0014), 12, 8),
                    lambda co, n: nh.lerp(nh.lerp(HEAD, SAND, 0.6), BAND, 0.15)))
        # heat pit between eye and nostril
        p, t, side, up, w, h = head_point(head_frames, 0.80, sx * 0.93, 0.02)
        out.append((oriented_ellipsoid(p, (side * sx, t, up), (0.0022, 0.0042, 0.0036), 8, 6), PIT))
        # nostril near the snout tip
        p, t, side, up, w, h = head_point(head_frames, 0.93, sx * 0.55, 0.42)
        out.append((oriented_ellipsoid(p, (side * sx, t, up), (0.0018, 0.0026, 0.002), 8, 6), PIT))

    # forked tongue flicking out of the front of the mouth
    _u, c, t, side, up, w, h = head_frames[-2]
    base = c - up * 0.008 - t * 0.008
    mid = base + t * 0.035 - up * 0.004
    fork = mid + t * 0.012 - up * 0.002
    out.append((nh.tube([base, mid, fork], [0.0024, 0.0019, 0.0016], sides=6), TONGUE))
    for sx in (1, -1):
        tip = fork + t * 0.016 + side * sx * 0.009 + up * (0.004 * sx)
        out.append((nh.tube([fork, fork + (tip - fork) * 0.5, tip], [0.0015, 0.0011, 0.0], sides=5), TONGUE))
    return out


def build():
    body, tail_tip, tail_dir, head_frames = loft()
    mb = nh.MeshBuilder()
    mb.add(body)
    for bm, col in details(head_frames, tail_tip, tail_dir):
        mb.add(bm, col)
    obj = mb.to_object("SpeckledRattlesnake", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


def closeup(path, target, dist, az, el, lens=60):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    target = Vector(target)
    cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "SpeckledRattlesnake", ground=(0.62, 0.55, 0.42), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, -0.15, 0.31), 0.32, 35, 18)
