"""
Procedural high-detail American alligator (Alligator mississippiensis) for the map.

A low sprawling alligator resting on its belly with a gentle S-curve through the body and
tail and the head slightly raised. The body, legs, feet, eye mounds and nostril mound are
fused into one seamless surface, then sculpted by displacement: parallel rows of keeled
osteoderm scutes down the back, a double then single crest of tall scutes along the
laterally flattened tail, pebbly flank scales, a grid of rectangular belly scales, and
the lip line of the broad U-shaped snout. Upper teeth, eyes, nostrils and claws are crisp
separate details placed on the fused surface.

Usage:
  blender --background --python tools/blender/american_alligator.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmericanAlligator.fbx (map style Ground: pivot on the
ground under the belly, facing -Y).
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

NAME = "AmericanAlligator"
VOXEL = 0.0205

# Body profile along Y (snout at -Y): centre height, half-width, half-height.
KEY_Y = [-1.51, -1.40, -1.28, -1.18, -1.08, -0.95, -0.75, -0.45, -0.15, 0.10, 0.30, 0.60, 0.95, 1.30, 1.62]
KEY_W = [0.085, 0.104, 0.148, 0.178, 0.165, 0.200, 0.268, 0.300, 0.285, 0.240, 0.170, 0.098, 0.054, 0.030, 0.017]
KEY_H = [0.042, 0.052, 0.074, 0.094, 0.100, 0.114, 0.140, 0.150, 0.146, 0.136, 0.124, 0.112, 0.092, 0.062, 0.024]
KEY_Z = [0.125, 0.130, 0.140, 0.150, 0.145, 0.140, 0.135, 0.135, 0.135, 0.130, 0.120, 0.100, 0.078, 0.058, 0.040]
SNOUT_TIP = -1.51

# Palette
BACK = (0.235, 0.245, 0.170)
BACK_LIGHT = (0.420, 0.420, 0.300)
GROOVE = (0.075, 0.080, 0.058)
FLANK = (0.360, 0.355, 0.245)
LOW_FLANK = (0.560, 0.530, 0.380)
BELLY = (0.790, 0.745, 0.585)
BELLY_LINE = (0.560, 0.520, 0.390)
JAW = (0.640, 0.600, 0.450)
BAND = (0.370, 0.350, 0.240)
TOOTH = (0.880, 0.840, 0.700)
CLAW = (0.110, 0.095, 0.075)


def interp(ys, vs, y):
    if y <= ys[0]:
        return vs[0]
    if y >= ys[-1]:
        return vs[-1]
    for i in range(len(ys) - 1):
        if ys[i] <= y <= ys[i + 1]:
            t = (y - ys[i]) / (ys[i + 1] - ys[i])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5  # soften the kinks
            return vs[i] + (vs[i + 1] - vs[i]) * t
    return vs[-1]


def cx(y):
    """Lateral S-curve of the spine; the tail sweeps off to one side."""
    s = max(0.0, (y - 0.1) / 1.5)
    return 0.035 * math.sin(2.0 * (y + 1.6)) + 0.30 * s * s


def W(y):
    return interp(KEY_Y, KEY_W, y)


def H(y):
    return interp(KEY_Y, KEY_H, y)


def CZ(y):
    return interp(KEY_Y, KEY_Z, y)


def belly_factor(y):
    # flat-bottomed torso and head, round tail
    return 0.85 + 0.15 * nh.smoothstep(0.2, 0.6, y)


def section_power(y):
    if y < -1.1:
        return 3.0   # boxy, flat-topped skull and snout
    if y > 0.4:
        return 2.2   # rounder, laterally flattened tail
    return 2.5


def ring_point(y, a, w, h, z, p):
    u, v = math.cos(a), math.sin(a)
    ex = 2.0 / p
    px = cx(y) + w * math.copysign(abs(u) ** ex, u)
    pz = z + h * math.copysign(abs(v) ** ex, v) * (belly_factor(y) if v < 0 else 1.0)
    return Vector((px, y, pz))


def body_loft(sides=48):
    """One closed tube from the rounded snout tip to the tail tip."""
    bm = bmesh.new()
    rings = []
    r = W(SNOUT_TIP)
    # U-shaped snout: a semicircle in top view
    tip_y = SNOUT_TIP - r
    rings.append([bm.verts.new(Vector((cx(tip_y), tip_y, CZ(SNOUT_TIP) - 0.004)))])
    for phi_deg in (78, 64, 50, 36, 22, 10):
        phi = math.radians(phi_deg)
        y = SNOUT_TIP - r * math.sin(phi)
        w = r * math.cos(phi)
        h = H(SNOUT_TIP) * math.cos(phi) ** 0.45
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, w, h, CZ(SNOUT_TIP), section_power(y)))
                      for k in range(sides)])
    y = SNOUT_TIP
    while y < 1.60:
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, W(y), H(y), CZ(y), section_power(y)))
                      for k in range(sides)])
        y += 0.014
    rings.append([bm.verts.new(Vector((cx(1.66), 1.66, CZ(1.62))))])

    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def foot(body, s, palm, toes, toe_len, toe_r, webbed):
    """Flat palm with toes fanned out from it (angles in degrees from -Y toward the outside)."""
    px, py, pz = palm
    body.add(nh.ellipsoid((px, py, pz), (0.052, 0.058, 0.022), subdivisions=3), FLANK)
    tips = []
    for ang, length in zip(toes, toe_len):
        a = math.radians(ang)
        d = Vector((s * math.sin(a), -math.cos(a), 0.0))
        base = Vector((px, py, pz)) + d * 0.025
        mid = base + d * length * 0.55 + Vector((0, 0, -0.004))
        tip = base + d * length + Vector((0, 0, -0.008))
        body.add(nh.tube([base, mid, tip], [toe_r, toe_r * 0.85, toe_r * 0.62], sides=10), FLANK)
        tips.append((tip, d))
    if webbed:
        # webbing between the toes, a little over half way out
        pts = [Vector((px, py, pz))]
        for ang, length in zip(toes, toe_len):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            pts.append(Vector((px, py, pz)) + d * (0.025 + length * 0.62))
        outline = [(p.x, p.y, pz - 0.004) for p in pts]
        if s < 0:
            outline = [outline[0]] + list(reversed(outline[1:]))
        body.add(nh.flat_panel(outline, thickness=0.036), FLANK)
    return tips


def limbs(body):
    claw_tips = []
    for s in (-1, 1):
        # front leg: shoulder -> elbow (out and down) -> wrist, sprawled
        y0 = -0.72
        c = cx(y0)
        sh = Vector((c + s * 0.16, y0, 0.13))
        el = Vector((c + s * 0.37, y0 - 0.04, 0.085))
        wr = Vector((c + s * 0.42, y0 - 0.15, 0.035))
        body.add(nh.tube([sh, (sh + el) / 2 + Vector((0, 0, 0.012)), el], [0.078, 0.062, 0.052], sides=16), FLANK)
        body.add(nh.ellipsoid(el, (0.052, 0.05, 0.048), subdivisions=2), FLANK)
        body.add(nh.tube([el, (el + wr) / 2, wr], [0.050, 0.043, 0.036], sides=14), FLANK)
        palm = (wr.x + s * 0.012, wr.y - 0.045, 0.022)
        claw_tips += foot(body, s, palm, toes=(-30, -10, 10, 32, 56), toe_len=(0.070, 0.085, 0.090, 0.082, 0.062),
                          toe_r=0.023, webbed=False)[:5]

        # hind leg: big thigh out to the side, knee forward, foot pointing forward-outward
        y1 = 0.10
        c = cx(y1)
        hip = Vector((c + s * 0.15, y1, 0.125))
        kn = Vector((c + s * 0.41, y1 - 0.09, 0.105))
        an = Vector((c + s * 0.47, y1 + 0.07, 0.035))
        body.add(nh.tube([hip, (hip + kn) / 2 + Vector((0, 0, 0.018)), kn], [0.105, 0.088, 0.066], sides=16), FLANK)
        body.add(nh.ellipsoid(kn, (0.062, 0.06, 0.058), subdivisions=2), FLANK)
        body.add(nh.tube([kn, (kn + an) / 2, an], [0.060, 0.050, 0.042], sides=14), FLANK)
        palm = (an.x + s * 0.025, an.y - 0.03, 0.022)
        claw_tips += foot(body, s, palm, toes=(-5, 18, 40, 62), toe_len=(0.105, 0.120, 0.112, 0.090),
                          toe_r=0.024, webbed=True)[:3]
    return claw_tips


def head_mounds(body):
    for s in (-1, 1):
        y = -1.235
        top = CZ(y) + H(y)
        # raised eye mound with a bony brow behind it
        body.add(nh.ellipsoid((cx(y) + s * 0.088, y, top - 0.004), (0.042, 0.052, 0.034), subdivisions=3), BACK)
        body.add(nh.ellipsoid((cx(y) + s * 0.092, y + 0.035, top - 0.002), (0.034, 0.030, 0.026), subdivisions=2), BACK)
    y = -1.548
    body.add(nh.ellipsoid((cx(y), y, CZ(SNOUT_TIP) + 0.036), (0.046, 0.034, 0.022), subdivisions=3), BACK)


# ---------------------------------------------------------------- sculpting / paint

def local(co):
    y = co.y
    w, h, z = max(W(y), 1e-3), max(H(y), 1e-3), CZ(y)
    u = (co.x - cx(y)) / w
    v = (co.z - z) / h
    return u, v


def frac(x):
    return x - math.floor(x)


def plate(phase, gap=0.16):
    """1 inside a scute, 0 in the groove between scutes (phase 0..1 along the row)."""
    d = 0.5 - abs(phase - 0.5)
    return nh.smoothstep(0.0, gap, d)


def scute_field(co, u, v):
    """Returns (height 0..1, groove 0..1) of the dorsal armour at this point."""
    y = co.y
    if v < 0.25 or abs(u) > 0.95:
        return 0.0, 0.0
    top = nh.smoothstep(0.25, 0.55, v)
    # nuchal scutes: two pairs of big ones just behind the skull
    if -1.08 < y < -0.92:
        best = 0.0
        for yc, rows in ((-1.035, (0.17, 0.42)), (-0.965, (0.16, 0.40))):
            for u0 in rows:
                for sgn in (-1, 1):
                    d = ((u - sgn * u0) / 0.13) ** 2 + ((y - yc) / 0.028) ** 2
                    best = max(best, math.exp(-d * 1.6) * 1.3)
        return best * top, 0.0
    if y < -0.92 or y > 1.64:
        return 0.0, 0.0
    if y < 0.32:
        period = 0.068
        phase = frac((y + 0.92) / period)
        rows = (0.08, 0.25, 0.42, 0.58, 0.73)
        width = 0.058
        along = plate(phase)
        best, cover = 0.0, 0.0
        for i, u0 in enumerate(rows):
            for sgn in (-1, 1):
                du = (u - sgn * u0) / width
                across = math.exp(-du * du)
                keel = math.exp(-(du / 0.4) ** 2)
                amp = 1.0 - 0.13 * i
                best = max(best, amp * along * (0.45 * across + 0.8 * keel))
                cover = max(cover, across)
        # dark seams both between transverse rows and between neighbouring scutes in a row
        groove = max(1.0 - along, 0.7 * nh.smoothstep(0.55, 0.15, cover))
        return best * top, groove * top
    # tail: tall crest scutes, a double row then a single row toward the tip
    period = 0.058
    phase = frac((y - 0.32) / period)
    along = plate(phase, gap=0.2)
    shrink = 1.0 - 0.6 * nh.smoothstep(0.32, 1.62, y)
    if y < 0.98:
        rows = (0.42,)
        best = 0.0
        for sgn in (-1, 1):
            du = (u - sgn * rows[0]) / 0.16
            best = max(best, math.exp(-du * du))
    else:
        du = u / 0.22
        best = math.exp(-du * du)
    # pointed plates: highest at the back edge of each scute
    point = 0.55 + 0.45 * phase
    return 2.5 * shrink * best * along * point * top, (1.0 - along) * top


def lip_line(co, u, v):
    """Distance-ish to the jaw line on the side of the head (0 = on the line)."""
    y = co.y
    if y > -1.08 or abs(u) < 0.45:
        return 1.0, 0.0
    h = H(min(max(y, SNOUT_TIP), -1.08))
    zj = jaw_z(y)
    d = abs(co.z - zj) / max(0.25 * h, 0.006)
    return d, zj


def jaw_z(y):
    yy = min(max(y, SNOUT_TIP - 0.08), -1.08)
    z = CZ(min(max(yy, SNOUT_TIP), -1.08))
    h = H(min(max(yy, SNOUT_TIP), -1.08))
    # the line curves up slightly at the back of the jaw (the "smile")
    back = nh.smoothstep(-1.28, -1.12, yy)
    return z - 0.06 * h + back * 0.28 * h


def sculpt(bm):
    """Displace the fused body along its normals and paint it."""
    bm.normal_update()
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    disp = {}
    paint = {}
    for vert in bm.verts:
        co = vert.co.copy()
        n = vert.normal.copy()
        u, v = local(co)
        y = co.y
        on_body = abs(u) < 1.12 and -1.3 < v < 1.4
        sc, groove = scute_field(co, u, v) if on_body else (0.0, 0.0)
        pebble = noise.noise(co * 42.0)
        coarse = noise.noise(co * 9.0 + Vector((3.1, 1.7, 0.4)))
        d = 0.0
        d += 0.017 * sc
        d -= 0.004 * groove
        d += 0.0035 * pebble
        # lip line groove on the side of the head
        ld, _ = lip_line(co, u, v)
        if ld < 1.0:
            d -= 0.007 * (1.0 - ld)
        # rectangular belly scales
        belly_t = nh.smoothstep(-0.25, -0.6, v) if on_body else (nh.smoothstep(-0.2, -0.7, n.z))
        line = 0.0
        if belly_t > 0.0 and y > -1.0:
            gx = frac((co.x - cx(y)) / 0.042)
            gy = frac(y / 0.034)
            line = max(1.0 - nh.smoothstep(0.0, 0.12, min(gx, 1 - gx)),
                       1.0 - nh.smoothstep(0.0, 0.12, min(gy, 1 - gy)))
            d -= 0.0025 * line * belly_t
        # head: bumpy skin and pressure-receptor dots on the snout
        if y < -1.08:
            d += 0.003 * noise.noise(co * 28.0)
        disp[vert] = n * d

        # ---- colour
        if on_body:
            t_back = nh.smoothstep(-0.05, 0.5, v + 0.08 * coarse)
            t_low = nh.smoothstep(0.05, -0.28, v + 0.08 * coarse)
            t_belly = nh.smoothstep(-0.26, -0.52, v + 0.06 * coarse)
        else:
            t_back = nh.smoothstep(0.0, 0.7, n.z)
            t_low = nh.smoothstep(0.1, -0.3, n.z)
            t_belly = nh.smoothstep(-0.3, -0.75, n.z)
        c = nh.lerp(nh.lerp(FLANK, LOW_FLANK, t_low), BACK, t_back)
        c = nh.lerp(c, BACK_LIGHT, min(1.0, sc * 0.55) * t_back)
        c = nh.lerp(c, GROOVE, 0.75 * groove * t_back)
        # irregular darker blotches on the back
        c = nh.lerp(c, GROOVE, 0.35 * nh.smoothstep(0.2, 0.6, coarse) * t_back)
        # tail: faint pale bands on the sides and top
        if y > 0.3:
            band = 0.5 + 0.5 * math.sin((y - 0.3) / 0.21 * math.tau)
            c = nh.lerp(c, BAND, 0.35 * nh.smoothstep(0.65, 1.0, band) * (1.0 - t_belly))
        # lower jaw is paler
        if y < -1.08 and on_body:
            zj = jaw_z(y)
            below = nh.smoothstep(zj + 0.004, zj - 0.012, co.z)
            c = nh.lerp(c, JAW, below)
            if ld < 1.0:
                c = nh.lerp(c, GROOVE, 0.85 * (1.0 - ld))
            # tiny dark sensory dots along the snout
            if noise.noise(co * 60.0) > 0.42:
                c = nh.lerp(c, GROOVE, 0.5)
        c = nh.lerp(c, BELLY, t_belly)
        c = nh.lerp(c, BELLY_LINE, 0.7 * line * t_belly)
        k = 0.88 + 0.22 * (0.5 + 0.5 * pebble) * (1.0 - 0.5 * t_belly)
        paint[vert] = (c[0] * k, c[1] * k, c[2] * k)

    for vert, dv in disp.items():
        vert.co += dv
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


def drop_islands(bm, min_verts=200):
    """Removes stray voxel fragments (e.g. where the tail tip gets thinner than a voxel)."""
    seen = set()
    for start in bm.verts:
        if start in seen:
            continue
        part, stack = [], [start]
        seen.add(start)
        while stack:
            v = stack.pop()
            part.append(v)
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in seen:
                    seen.add(o)
                    stack.append(o)
        if len(part) < min_verts:
            bmesh.ops.delete(bm, geom=part, context="VERTS")


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def cone(base, tip, r, sides=8):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


def teeth(mb, surf):
    """Only the upper teeth show along the closed jaw, over the lower lip."""
    spots = []
    # around the rounded tip
    c = Vector((cx(SNOUT_TIP), SNOUT_TIP, 0.0))
    for beta in (-72, -50, -28, -9, 9, 28, 50, 72):
        b = math.radians(beta)
        d = Vector((math.sin(b), -math.cos(b), 0.0))
        spots.append((c + d * 0.4, -d, SNOUT_TIP - 0.05))
    # along both sides
    y = -1.48
    while y < -1.17:
        for s in (-1, 1):
            spots.append((Vector((cx(y) + s * 0.5, y, 0.0)), Vector((-s, 0.0, 0.0)), y))
        y += 0.027
    for origin, direction, yy in spots:
        z = jaw_z(yy) + 0.003
        o = Vector((origin.x, origin.y, z))
        loc, normal = surf.hit(o, direction)
        if loc is None:
            continue
        big = math.exp(-((yy + 1.43) / 0.03) ** 2) + 0.8 * math.exp(-((yy + 1.30) / 0.03) ** 2)
        length = 0.013 + 0.011 * big + 0.004 * noise.noise(loc * 50.0)
        out = Vector((normal.x, normal.y, 0.0))
        out = out.normalized() if out.length > 1e-4 else Vector((0, 0, 0))
        base = loc - out * 0.003
        tip = loc + Vector((0, 0, -length)) + out * 0.004
        mb.add(cone(base, tip, 0.0058 + 0.0028 * big), TOOTH)


def eyes(mb, surf):
    for s in (-1, 1):
        y = -1.245
        top = CZ(y) + H(y)
        centre = Vector((cx(y) + s * 0.100, y - 0.016, top + 0.002))
        look = Vector((s * 0.75, -0.35, 0.55)).normalized()
        side = look.cross(Vector((0, 0, 1))).normalized()

        def eye_col(co, n, centre=centre, look=look, side=side):
            d = (co - centre).normalized()
            k = d.dot(look)
            if k > 0.8 and abs((co - centre).dot(side)) < 0.0035:
                return (0.02, 0.02, 0.015)          # vertical slit pupil
            if k > 0.55:
                return (0.50, 0.44, 0.13)           # yellow-green iris
            return (0.07, 0.07, 0.05)
        mb.add(nh.ellipsoid(centre, (0.016, 0.019, 0.014), subdivisions=3), eye_col)


def nostrils(mb, surf):
    y = -1.553
    for s in (-1, 1):
        loc, _n = surf.hit((cx(y) + s * 0.016, y, 0.5), (0, 0, -1))
        if loc is None:
            continue
        mb.add(nh.ellipsoid(loc + Vector((0, 0, 0.001)), (0.0085, 0.0055, 0.004), subdivisions=2), (0.02, 0.02, 0.015))


def claws(mb, tips):
    for tip, d in tips:
        base = tip - d * 0.008 + Vector((0, 0, 0.004))
        end = tip + d * 0.026 + Vector((0, 0, -0.007))
        mb.add(nh.tube([base, base + d * 0.014, end], [0.0085, 0.0065, 0.0], sides=8), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    body = nh.MeshBuilder()
    body.add(body_loft(), FLANK)
    claw_tips = limbs(body)
    head_mounds(body)
    fused = body.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    drop_islands(fused)
    fused = sculpt(fused)

    surf = Surface(fused)
    mb = nh.MeshBuilder()
    teeth(mb, surf)
    eyes(mb, surf)
    nostrils(mb, surf)
    claws(mb, claw_tips)
    mb.add(fused)
    obj = mb.to_object(NAME, roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


def render_extra(obj, path):
    """Head close-up, using the camera and light set up by nh.render_preview."""
    scene = bpy.context.scene
    cam = scene.camera
    zmin = 0.0  # already grounded
    target = Vector((cx(-1.36), -1.36, 0.16 + zmin))
    for i, (az, el, dist) in enumerate(((38, 22, 0.95), (-70, 12, 0.85))):
        a, e = math.radians(az), math.radians(el)
        cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        out = Path(path)
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, NAME)
    if "--render" in argv:
        path = argv[argv.index("--render") + 1]
        nh.render_preview(obj, path, ground=(0.40, 0.38, 0.28),
                          views=((35, 25), (-90, 8), (25, 62)))
        render_extra(obj, path)


if __name__ == "__main__":
    main()
