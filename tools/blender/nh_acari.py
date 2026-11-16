"""
Shared builder for the acarine (tick and mite) models: ixodes_scapularis.py,
amblyomma_americanum.py, haemaphysalis_longicornis.py, ornithonyssus_bacoti.py and
leptotrombidium_deliense.py.

Ticks and mites are arachnids whose body is fused into just two parts:
  * the gnathosoma (the "capitulum" of ticks) in front: a basis carrying the paired
    chelicerae and, in ticks, the toothed hypostome, flanked by two palps;
  * the idiosoma behind it: a flattened oval (egg-shaped in ticks) that bears the
    legs and is hardened by a dorsal plate (the scutum of hard ticks, the dorsal
    shield or scutum of mites), with festoons along the rear margin of many ticks
    and setae (bristles, plumose in chiggers) on mites.
  Adults and nymphs have eight legs, larvae six. Each leg: a coxa under the body,
  then femur, genu/tibia and tarsus segments ending in a pair of hooked claws.

  * build(spec, pose) -> MeshBuilder with the animal in its own frame: faces -Y,
    body centred over the origin, the substrate is the plane z = 0.
      pose "walk":  standing with every foot on z = 0 (Ground style).
      pose "quest": clinging lengthwise to a narrow perch under its belly (a grass
                    blade of half-width spec.grip), legs II-IV hooked round its edges
                    and legs I held out forward and up, the way ticks wait for a host.
    The returned builder's bmesh can be transformed and added to another builder
    with add(builder.bm) (colours are kept).
  * grass_blade(): a flat tapering blade whose upper part runs straight along a given
    line, as the questing perch; questing_perch() places a questing tick on one.
  * The idiosoma is painted by Spec.paint(xn, yn, r, co, n) (normalised body
    coordinates: xn across, yn front -1 .. rear +1, r = 0 centre .. 1 margin); the
    default is a glossy body_color with a paler margin. The dorsal plate likewise by
    Spec.scutum_paint.
  * The gloss is baked into the vertex colours (the map shader is diffuse only).
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh

LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()


@dataclass
class Spec:
    name: str
    kind: str = "tick"              # "tick" (capitulum with hypostome) or "mite"
    length: float = 0.5             # idiosoma length (Y)
    width: float = 0.36             # idiosoma full width (X)
    height: float = 0.06            # dorsal dome above the margin
    belly: float = 0.025            # ventral bulge below the margin
    rim: float = 0.018              # thickness of the body margin
    egg: float = 0.22               # > 0: broader behind
    hump: float = 0.15              # rear of the dome higher than the front
    clearance: float = 0.05         # walk pose: belly above the ground

    body_color: tuple = (0.6, 0.2, 0.1)
    belly_color: tuple = (0.35, 0.12, 0.06)
    margin_color: Optional[tuple] = None
    gloss: float = 0.35
    paint: Optional[Callable] = None            # fn(xn, yn, r, co, n) -> rgb

    # dorsal plate: centre yn, half-length and half-width (normalised), posterior point
    scutum: Optional[tuple] = (-0.45, 0.55, 0.62, 0.0)
    scutum_color: tuple = (0.08, 0.05, 0.04)
    scutum_paint: Optional[Callable] = None     # fn(xn, yn, s, co, n) -> rgb, s = 0 centre .. 1 edge
    scutum_lift: float = 0.006
    spot: Optional[tuple] = None                # (colour, radius as a fraction of width): scutum tip spot
    eyes: Optional[tuple] = None                # (colour, [(xn, yn), ...]) flat eyes on the dorsum

    festoons: int = 0
    festoon_arc: float = 1.05                   # half-angle (radians) of the rear arc they span
    festoon_color: Optional[tuple] = None

    # gnathosoma
    basis_len: float = 0.07
    basis_w: float = 0.11
    basis_h: float = 0.04
    hypo_len: float = 0.10                      # hypostome (ticks) / chelicerae (mites)
    palp_len: float = 0.11
    palp_w: float = 0.022
    palp_flare: float = 0.0                     # lateral angle of the palps (Haemaphysalis)
    mouth_color: tuple = (0.10, 0.06, 0.04)
    palp_color: Optional[tuple] = None
    hypo_color: Optional[tuple] = None

    # legs: per pair, front to back
    leg_y: tuple = (-0.55, -0.35, -0.15, 0.05)  # coxa positions (yn)
    leg_angle: tuple = (30, 70, 110, 145)       # walk: degrees from straight ahead
    leg_len: tuple = (0.42, 0.40, 0.42, 0.46)
    leg_r: float = 0.016
    knee: float = 0.10                          # walk: knee height above the body margin (abs.)
    leg_color: tuple = (0.08, 0.05, 0.04)
    leg_joint: Optional[tuple] = None
    leg_tip: Optional[tuple] = None
    leg1_raised: float = 0.0                    # walk: lift leg I's foot (sensory leg of mites)
    claw_color: tuple = (0.05, 0.03, 0.02)
    leg_setae: int = 0                          # setae per leg segment

    # setae on the dorsum: rows of (yn, count, xn half-spread)
    setae: tuple = ()
    seta_len: float = 0.06
    seta_r: float = 0.004
    seta_color: tuple = (0.9, 0.9, 0.85)
    plumose: bool = False

    grip: float = 0.045                         # quest pose: half-width of the perch under it
    extra: dict = field(default_factory=dict)


def glossy(base, dark, n, gloss=0.35, shine=(0.85, 0.8, 0.75), sharp=14):
    c = nh.lerp(dark, base, nh.smoothstep(-0.5, 0.55, n.z))
    h = max(0.0, n.dot(LIGHT_DIR)) ** sharp
    return nh.lerp(c, shine, h * gloss)


def festoon_groove(spec, xn, yn):
    """0..1: how much (xn, yn) lies in a groove of the festoon row along the rear margin
    (the radial grooves between festoons plus the line marking off their inner ends)."""
    if not spec.festoons:
        return 0.0
    r = math.hypot(xn, yn)
    if r < 0.78:
        return 0.0
    th = math.atan2(xn, -yn) % math.tau
    a0 = math.pi - spec.festoon_arc
    if not a0 - 0.05 < th < math.pi + spec.festoon_arc + 0.05:
        return 0.0
    ph = (th - a0) / (2 * spec.festoon_arc) * spec.festoons
    radial = math.exp(-((ph - round(ph)) / 0.2) ** 2) * nh.smoothstep(0.80, 0.88, r)
    inner = math.exp(-((r - 0.84) / 0.022) ** 2) * (0.0 <= ph <= spec.festoons)
    return max(radial, inner)


class Body:
    """Idiosoma geometry as a height field over its egg-shaped outline."""

    def __init__(self, spec, zc):
        self.s = spec
        self.zc = zc

    def half_w(self, yn):
        return self.s.width * 0.5 * (1.0 + self.s.egg * yn)

    def xy(self, xn, yn):
        return xn * self.half_w(yn), yn * self.s.length * 0.5

    def norm(self, x, y):
        yn = y / (self.s.length * 0.5)
        return x / self.half_w(max(-1.0, min(1.0, yn))), yn

    def r(self, x, y):
        xn, yn = self.norm(x, y)
        return math.hypot(xn, yn)

    def top(self, x, y):
        xn, yn = self.norm(x, y)
        r = min(1.0, math.hypot(xn, yn))
        s = self.s
        return self.zc + s.rim * 0.5 + s.height * (1.0 - r * r) ** 0.6 * (1.0 + s.hump * yn)

    def top_normal(self, x, y):
        e = 0.004
        dx = (self.top(x + e, y) - self.top(x - e, y)) / (2 * e)
        dy = (self.top(x, y + e) - self.top(x, y - e)) / (2 * e)
        return Vector((-dx, -dy, 1.0)).normalized()

    def top_point(self, xn, yn, lift=0.0):
        x, y = self.xy(xn, yn)
        return Vector((x, y, self.top(x, y) + lift))

    def shell(self, nr=8, na=60):
        s = self.s
        bm = bmesh.new()

        # with festoons, crowd the vertices towards the rear margin so the grooves read
        warp = 0.7 if s.festoons else 0.0

        def ring(r, z_fn):
            out = []
            for k in range(na):
                u = k / na * math.tau
                th = u + warp * math.sin(u)
                yn, xn = -r * math.cos(th), r * math.sin(th)
                g = festoon_groove(s, xn, yn) if r > 0.95 else 0.0
                x, y = self.xy(xn * (1.0 - 0.06 * g), yn * (1.0 - 0.06 * g))
                z = z_fn(x, y, r, yn)
                if r <= 1.0:
                    gz = festoon_groove(s, xn, yn)
                    z += -0.7 * s.rim * gz if z > self.zc else 0.0
                out.append(bm.verts.new((x, y, z)))
            return out

        top_z = lambda x, y, r, yn: self.top(x, y)
        bot_z = lambda x, y, r, yn: self.zc - s.rim * 0.5 - s.belly * (1.0 - min(1.0, r) ** 2) ** 0.5
        rs = [math.sin(k / nr * math.pi / 2) for k in range(1, nr + 1)]
        tops = [ring(r, top_z) for r in rs]
        eq = ring(1.0 + s.rim / s.width, lambda x, y, r, yn: self.zc)
        bots = [ring(r, bot_z) for r in reversed(rs)]
        ct = bm.verts.new((0, 0, self.top(0, 0)))
        cb = bm.verts.new((0, 0, bot_z(0, 0, 0, 0)))
        seq = tops + [eq] + bots
        for k in range(na):
            j = (k + 1) % na
            bm.faces.new([ct, seq[0][k], seq[0][j]])
            bm.faces.new([cb, seq[-1][j], seq[-1][k]])
            for a, b in zip(seq, seq[1:]):
                bm.faces.new([a[k], b[k], b[j], a[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm

    def cap(self, boundary, lift, rings=5, sides=28):
        """Thin plate hugging the dorsum. boundary(s, phi) -> (xn, yn)."""
        bm = bmesh.new()

        def pt(s, phi):
            xn, yn = boundary(s, phi)
            r = math.hypot(xn, yn)
            if r > 0.985:
                xn, yn = xn * 0.985 / r, yn * 0.985 / r
            x, y = self.xy(xn, yn)
            return Vector((x, y, self.top(x, y))) + self.top_normal(x, y) * lift

        c = bm.verts.new(pt(0.0, 0.0))
        prev = None
        for k in range(1, rings + 1):
            s = k / rings
            ring = [bm.verts.new(pt(s, i / sides * math.tau)) for i in range(sides)]
            for i in range(sides):
                j = (i + 1) % sides
                bm.faces.new([c, ring[i], ring[j]] if prev is None else [prev[i], ring[i], ring[j], prev[j]])
            prev = ring
        # a little edge wall so the plate reads as raised
        low = [bm.verts.new(v.co - Vector((0, 0, lift * 1.6))) for v in prev]
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new([prev[i], low[i], low[j], prev[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm


def scutum_boundary(spec):
    cy, hl, hw, point = spec.scutum

    def b(s, phi):
        back = max(0.0, -math.cos(phi))
        m = 1.0 + point * back ** 3
        yn = cy - s * math.cos(phi) * hl * m
        xn = s * math.sin(phi) * hw * (1.0 - 0.45 * point * back ** 2)
        return xn, yn
    return b


def scutum_tip(spec):
    cy, hl, hw, point = spec.scutum
    return cy + hl * (1.0 + point)


# ---------------------------------------------------------------- appendages

def ball(c, r, color, mb, seg=6, rings=3):
    mb.add(nh.uv_ellipsoid(c, (r, r, r), seg, rings), color)


def seta(mb, base, direction, length, r, color, plumose=False):
    d = direction.normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    bend = d.cross(side).normalized()
    mid = base + d * length * 0.55 + bend * length * 0.06
    tip = base + d * length + bend * length * 0.15
    mb.add(nh.tube([base, mid, tip], [r, r * 0.75, 0.0], sides=3), color, smooth=False)
    if plumose:
        for f in (0.45, 0.78):
            p = base.lerp(mid, f / 0.55) if f < 0.55 else mid.lerp(tip, (f - 0.55) / 0.45)
            for sx in (-1, 1):
                q = p + (side * sx * 0.8 + d * 0.6).normalized() * length * 0.22
                mb.add(nh.tube([p, q], [r * 0.6, 0.0], sides=3, cap_start=False), color, smooth=False)


def jointed(mb, pts, radii, spec, colors=None, sides=6):
    joint = spec.leg_joint or spec.leg_color
    for i in range(len(pts) - 1):
        c = colors[i] if colors else spec.leg_color
        if callable(c):
            col = c
        else:
            col = (lambda co, n, c=c: glossy(c, nh.lerp(c, (0, 0, 0), 0.5), n, spec.gloss))
        mb.add(nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=sides), col)
        if 0 < i < len(pts) - 1:
            ball(pts[i], radii[i] * 1.12, joint, mb)


def claws(mb, foot, d, spec):
    d = d.normalized()
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    down = d.cross(side).normalized()
    if down.z > 0:
        down = -down
    cl = spec.leg_r * 2.6
    for sx in (-1, 1):
        p0 = foot
        p1 = foot + d * cl * 0.6 + side * sx * cl * 0.35
        p2 = p1 + d * cl * 0.3 + down * cl * 0.5
        mb.add(nh.tube([p0, p1, p2], [spec.leg_r * 0.4, spec.leg_r * 0.3, 0.0], sides=4), spec.claw_color,
               smooth=False)


def leg_setae(mb, pts, spec):
    if not spec.leg_setae:
        return
    for a, b in zip(pts[:-1], pts[1:]):
        d = (b - a)
        for k in range(spec.leg_setae):
            f = (k + 0.6) / (spec.leg_setae + 0.2)
            base = a.lerp(b, f)
            out = Vector((d.y, -d.x, 0)).normalized() * (1 if k % 2 else -1)
            direction = d.normalized() * 0.8 + out * 0.5 + Vector((0, 0, 0.6))
            seta(mb, base + Vector((0, 0, spec.leg_r * 0.6)), direction, spec.seta_len * 0.7,
                 spec.seta_r * 0.85, spec.seta_color, spec.plumose)


def legs(mb, spec, body, pose):
    s_ = spec
    zh = body.zc - s_.rim * 0.5 - s_.belly * 0.35
    feet = []
    for i, (yn, ang, L) in enumerate(zip(s_.leg_y, s_.leg_angle, s_.leg_len)):
        for s in (-1, 1):
            hw = body.half_w(yn) * math.sqrt(max(0.0, 1.0 - yn * yn))
            h = Vector((s * hw * 0.55, yn * s_.length * 0.5, zh))
            r0 = s_.leg_r
            radii = [r0 * 1.25, r0 * 1.15, r0, r0 * 0.8, r0 * 0.55]
            if pose == "quest" and i == 0:
                a = math.radians(spec.extra.get("quest_spread", 38))
                d = Vector((s * math.sin(a), -math.cos(a), 0))
                up = Vector((0, 0, 1))
                pts = [h, h + d * L * 0.18 + up * L * 0.05, h + d * L * 0.46 + up * L * 0.20,
                       h + d * L * 0.76 + up * L * 0.36, h + d * L * 1.0 + up * L * 0.52]
            elif pose == "quest":
                # II reaches forward, IV back, so the gripping legs radiate round the body
                dy = (-0.30, 0.0, 0.34)[i - 1] * L
                g = s_.grip
                knee_x = hw + L * 0.20
                pts = [h, Vector((s * (hw * 0.55 + L * 0.12), h.y + dy * 0.25, zh + L * 0.05)),
                       Vector((s * knee_x, h.y + dy * 0.55, body.zc + L * 0.14)),
                       Vector((s * (knee_x + L * 0.10), h.y + dy * 0.9, body.zc - L * 0.12)),
                       Vector((s * (g + L * 0.02), h.y + dy, -0.03))]
            else:
                a = math.radians(ang)
                d = Vector((s * math.sin(a), -math.cos(a), 0))
                knee_z = body.zc + s_.knee
                foot_z = 0.004 + (s_.leg1_raised if i == 0 else 0.0)
                p1 = h + d * L * 0.16
                p1.z = nh.lerp((zh,), (knee_z,), 0.55)[0]
                p2 = h + d * L * 0.44
                p2.z = knee_z
                p3 = h + d * L * 0.76
                p3.z = nh.lerp((knee_z,), (foot_z,), 0.5)[0]
                p4 = h + d * L
                p4.z = foot_z
                pts = [h, p1, p2, p3, p4]
            tip = s_.leg_tip or s_.leg_color
            cols = [s_.leg_color, s_.leg_color, s_.leg_color, tip]
            jointed(mb, pts, radii, s_, cols)
            claws(mb, pts[-1], pts[-1] - pts[-2], s_)
            leg_setae(mb, pts[1:], s_)
            feet.append(pts[-1])
    return zh, feet


def gnathosoma(mb, spec, body):
    s = spec
    zc = body.zc
    y0 = -s.length * 0.5
    dark = nh.lerp(s.mouth_color, (0, 0, 0), 0.5)
    mcol = lambda co, n: glossy(s.mouth_color, dark, n, s.gloss)
    pc = s.palp_color or s.mouth_color
    pcol = lambda co, n: glossy(pc, nh.lerp(pc, (0, 0, 0), 0.5), n, s.gloss)
    hc = s.hypo_color or nh.lerp(s.mouth_color, (0.8, 0.7, 0.6), 0.25)

    def squarish(n):
        return 1.0 + 0.16 * (abs(n.x) ** 3 + abs(n.y) ** 3)
    bc = Vector((0, y0 - s.basis_len * 0.3, zc + s.rim * 0.2))
    mb.add(nh.uv_ellipsoid(bc, (s.basis_w * 0.5, s.basis_len * 0.62, s.basis_h * 0.5), 12, 8, deform=squarish),
           mcol)
    yb = y0 - s.basis_len * 0.82
    zb = zc - s.basis_h * 0.05
    if s.kind == "tick":
        # toothed hypostome under the paired chelicerae
        h0 = Vector((0, yb + 0.01, zb - 0.006))
        h1 = Vector((0, yb - s.hypo_len, zb - 0.012))
        mb.add(nh.tube([h0, h0.lerp(h1, 0.6), h1], [s.palp_w * 0.75, s.palp_w * 0.6, 0.0], sides=6,
                       scale_xy=(1.0, 0.55)), hc)
        for sx in (-1, 1):
            c0 = Vector((sx * s.palp_w * 0.35, yb + 0.01, zb + 0.006))
            c1 = Vector((sx * s.palp_w * 0.25, yb - s.hypo_len * 0.85, zb + 0.002))
            mb.add(nh.tube([c0, c1], [s.palp_w * 0.32, s.palp_w * 0.12], sides=5), dark)
        # palps
        for sx in (-1, 1):
            b0 = Vector((sx * s.basis_w * 0.30, yb + 0.012, zb + 0.004))
            tip = Vector((sx * s.palp_w * 0.95, yb - s.palp_len, zb))
            if s.palp_flare > 0:
                # short palps whose second article juts out sideways into a point
                corner = Vector((sx * (s.basis_w * 0.5 + s.palp_flare), yb - s.palp_len * 0.30, zb + 0.003))
                pts = [b0, b0.lerp(corner, 0.6), b0.lerp(tip, 0.7) + Vector((sx * s.palp_flare * 0.45, 0, 0)), tip]
                radii = [s.palp_w * 0.8, s.palp_w * 1.15, s.palp_w * 0.9, s.palp_w * 0.3]
                mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.55)), pcol)
                # the pointed lateral salient of palp article 2, jutting out and back
                c0 = b0.lerp(corner, 0.45)
                spur = corner + Vector((sx * s.palp_w * 0.9, s.palp_w * 1.2, 0))
                mb.add(nh.tube([c0, corner, spur], [s.palp_w * 0.8, s.palp_w * 0.45, 0.0],
                               sides=5, scale_xy=(1.0, 0.5)), pcol)
            else:
                pts = [b0, b0.lerp(tip, 0.22), b0.lerp(tip, 0.6) + Vector((sx * s.palp_w * 0.25, 0, 0.002)),
                       tip]
                radii = [s.palp_w * 0.8, s.palp_w * 0.95, s.palp_w * 1.05, s.palp_w * 0.45]
                mb.add(nh.tube(pts, radii, sides=7, scale_xy=(1.0, 0.75)), pcol)
                # article joints
                ball(b0.lerp(tip, 0.22), s.palp_w * 0.98, dark, mb)
    else:
        # mite: paired chelicerae forward, leg-like palps either side
        for sx in (-1, 1):
            c0 = Vector((sx * s.basis_w * 0.15, yb + 0.01, zb + 0.004))
            c1 = Vector((sx * s.basis_w * 0.10, yb - s.hypo_len, zb - 0.004))
            mb.add(nh.tube([c0, c0.lerp(c1, 0.5), c1], [s.palp_w * 0.5, s.palp_w * 0.4, 0.0], sides=5), hc)
            # curved cheliceral blade / digit at the tip
            hook = c1 + Vector((0, -s.palp_w * 0.3, -s.palp_w * 0.9))
            mb.add(nh.tube([c1 + Vector((0, s.palp_w * 0.6, 0)), c1, hook], [s.palp_w * 0.3, s.palp_w * 0.22, 0],
                           sides=4), dark, smooth=False)
            b0 = Vector((sx * s.basis_w * 0.38, yb + 0.015, zb))
            out = Vector((sx * (s.basis_w * 0.5 + s.palp_flare), 0, 0))
            pts = [b0, b0 + out * 0.5 + Vector((0, -s.palp_len * 0.35, s.palp_w)),
                   b0 + out + Vector((0, -s.palp_len * 0.7, s.palp_w * 0.6)),
                   b0 + out * 0.8 + Vector((0, -s.palp_len, -s.palp_w * 0.4))]
            radii = [s.palp_w, s.palp_w * 0.95, s.palp_w * 0.8, s.palp_w * 0.45]
            jointed(mb, pts, radii, s, [pc] * 3, sides=6)
            if s.extra.get("palp_claw"):
                tip = pts[-1]
                for k in (-1, 0, 1):
                    q = tip + Vector((-sx * s.palp_w * 0.5 + k * s.palp_w * 0.35, -s.palp_w * 0.9, -s.palp_w * 1.1))
                    mb.add(nh.tube([tip, q], [s.palp_w * 0.3, 0.0], sides=4), dark, smooth=False)
            if s.leg_setae:
                seta(mb, pts[2], Vector((sx * 0.6, -0.8, 0.6)), s.seta_len * 0.7, s.seta_r * 0.85, s.seta_color,
                     s.plumose)


def default_paint(spec):
    margin = spec.margin_color or nh.lerp(spec.body_color, (1, 1, 1), 0.15)

    def paint(xn, yn, r, co, n):
        c = glossy(spec.body_color, spec.belly_color, n, spec.gloss)
        c = nh.lerp(c, margin, 0.6 * nh.smoothstep(0.86, 0.98, r) * (n.z > -0.2))
        k = 0.94 + 0.12 * noise.noise(co * 40)
        return tuple(min(1.0, x * k) for x in c)
    return paint


def build(spec, pose="walk"):
    """The animal in its own frame (faces -Y, substrate z = 0). Returns (builder, info)."""
    s = spec
    zc = (s.clearance if pose == "walk" else 0.004) + s.belly + s.rim * 0.5
    body = Body(s, zc)
    mb = nh.MeshBuilder()

    paint = s.paint or default_paint(s)

    groove = nh.lerp(s.belly_color, (0, 0, 0), 0.45)

    def body_col(co, n):
        xn, yn = body.norm(co.x, co.y)
        r = math.hypot(xn, yn)
        c = paint(xn, yn, r, co, n)
        if s.festoons and n.z > -0.3:
            th = math.atan2(xn, -yn) % math.tau
            if r > 0.84 and abs(th - math.pi) < s.festoon_arc and s.festoon_color:
                c = nh.lerp(c, glossy(s.festoon_color, s.belly_color, n, s.gloss), 0.8)
            c = nh.lerp(c, groove, 0.9 * festoon_groove(s, xn, yn))
        return c
    mb.add(body.shell(na=60 if s.festoons else 44), body_col)

    if s.scutum:
        sc = s.scutum_color
        sp = s.scutum_paint or (lambda xn, yn, t, co, n: glossy(sc, nh.lerp(sc, (0, 0, 0), 0.4), n, s.gloss * 1.3))
        bnd = scutum_boundary(s)
        cy, hl, hw, _ = s.scutum

        def scut_col(co, n):
            xn, yn = body.norm(co.x, co.y)
            t = math.hypot(xn / hw, (yn - cy) / hl)
            return sp(xn, yn, t, co, n)
        mb.add(body.cap(bnd, s.scutum_lift), scut_col)
        if s.spot:
            col, rad = s.spot
            ty = scutum_tip(s) - rad * 1.6
            rn = rad * s.width / body.half_w(ty) * 1.0
            mb.add(body.cap(lambda t, phi: (t * math.sin(phi) * rn, ty - t * math.cos(phi) * rad * 2.2),
                            s.scutum_lift * 1.6, rings=3, sides=16),
                   lambda co, n: glossy(col, nh.lerp(col, (0.3, 0.3, 0.3), 0.5), n, 0.3))
    if s.eyes:
        col, pos = s.eyes
        for xn, yn in pos:
            for sx in (-1, 1):
                mb.add(body.cap(lambda t, phi, xn=xn, yn=yn, sx=sx: (sx * xn + t * math.sin(phi) * 0.07,
                                                                     yn - t * math.cos(phi) * 0.06),
                                s.scutum_lift * 1.8, rings=2, sides=10),
                       lambda co, n, col=col: glossy(col, nh.lerp(col, (0, 0, 0), 0.4), n, 0.6))

    gnathosoma(mb, s, body)
    hip_z, feet = legs(mb, s, body, pose)

    for yn, count, spread in s.setae:
        for k in range(count):
            xn = 0.0 if count == 1 else -spread + 2 * spread * k / (count - 1)
            base = body.top_point(xn, yn, -0.002)
            nrm = body.top_normal(base.x, base.y)
            d = nrm + Vector((xn * 0.5, 0.55, 0))
            seta(mb, base, d, s.seta_len, s.seta_r, s.seta_color, s.plumose)

    return mb, {"body": body, "hip_z": hip_z, "feet": feet}


# ---------------------------------------------------------------- perch

def grass_blade(mb, base, junction, direction, tip_len, width=0.05, thickness=0.012,
                color=(0.30, 0.52, 0.16), tip_color=(0.62, 0.66, 0.30), rise=0.45, steps=14):
    """Flat blade: cubic curve up from `base` (vertical) to `junction`, then straight along
    `direction` for tip_len to a point. Width lies along X; the top face is the side the
    curve's normal (tangent x X) points to. The top surface passes through the centreline."""
    B, J = Vector(base), Vector(junction)
    D = Vector(direction).normalized()
    h = (J - B).length
    P1 = B + Vector((0, 0, h * rise))
    P2 = J - D * h * 0.35
    pts = []
    for k in range(steps + 1):
        t = k / steps
        u = 1 - t
        pts.append(B * u ** 3 + P1 * 3 * u * u * t + P2 * 3 * u * t * t + J * t ** 3)
    for k in range(1, 6):
        pts.append(J + D * tip_len * k / 5)
    n_pts = len(pts)
    bm = bmesh.new()
    X = Vector((1, 0, 0))
    rows = []
    for i, p in enumerate(pts):
        tan = (pts[min(i + 1, n_pts - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = tan.cross(X).normalized()
        if nrm.z < 0 and i > n_pts - 8:
            nrm = -nrm
        t = i / (n_pts - 1)
        w = width * (1.15 - 0.25 * t) * (1.0 if i < n_pts - 5 else (n_pts - 1 - i) / 5 * 0.9 + 0.05)
        c = p - nrm * thickness * 0.5
        mid_top = c + nrm * thickness * 0.2
        rows.append([bm.verts.new(c + X * -w + nrm * thickness * 0.5), bm.verts.new(mid_top),
                     bm.verts.new(c + X * w + nrm * thickness * 0.5),
                     bm.verts.new(c + X * w - nrm * thickness * 0.5), bm.verts.new(c - nrm * thickness * 0.7),
                     bm.verts.new(c + X * -w - nrm * thickness * 0.5)])
    for a, b in zip(rows, rows[1:]):
        for k in range(6):
            j = (k + 1) % 6
            bm.faces.new([a[k], b[k], b[j], a[j]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    zmax = max(p.z for p in pts)
    mb.add(bm, lambda co, n: nh.lerp(color, tip_color, nh.smoothstep(zmax * 0.4, zmax, co.z)))


def tuft(mb, rng, centre, count=6, height=(0.18, 0.32), color=(0.30, 0.50, 0.15)):
    for k in range(count):
        a = k / count * math.tau + rng.uniform(0, 0.8)
        b = Vector(centre) + Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0))
        hgt = rng.uniform(*height)
        mid = b + Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, hgt * 0.6))
        tip = b + Vector((math.cos(a) * 0.14, math.sin(a) * 0.14, hgt))
        mb.add(nh.tube([b, mid, tip], [0.016, 0.011, 0.0], sides=3, scale_xy=(1.0, 0.35)), color)


def questing_perch(spec, pitch=34, anchor=(0.0, -0.05, 1.0), blade_base=(0.0, 0.32, 0.0), rng=None,
                   blade_color=(0.30, 0.52, 0.16), blade_tip=(0.62, 0.66, 0.30)):
    """A questing tick on the tip of a grass blade, with a tuft at its foot.
    pitch: degrees the tick's nose is raised. Returns the MeshBuilder (ground at z = 0)."""
    import random
    rng = rng or random.Random(5)
    tick, info = build(spec, pose="quest")
    R = Matrix.Rotation(-math.radians(pitch), 4, "X")
    T = Vector(anchor)
    nh.transform(tick.bm, Matrix.Translation(T) @ R)
    fwd = (R.to_3x3() @ Vector((0, -1, 0))).normalized()
    L = spec.length
    J = T - fwd * L * 0.62               # behind the tick's rear
    out = nh.MeshBuilder()
    grass_blade(out, blade_base, J, fwd, L * 0.62 + L * 0.40, width=spec.grip, color=blade_color,
                tip_color=blade_tip)
    # a couple of shorter companion blades and a tuft round the foot
    for dx, h, lean in ((-0.16, 0.55, 0.25), (0.15, 0.45, -0.2)):
        b = Vector(blade_base) + Vector((dx, 0.04, 0))
        j = b + Vector((lean * 0.3, -0.1, h))
        grass_blade(out, b, j, Vector((lean, -0.35, 1.0)), h * 0.35, width=spec.grip * 0.8, color=blade_color,
                    tip_color=blade_tip, steps=8)
    tuft(out, rng, blade_base, color=nh.lerp(blade_color, (0.2, 0.3, 0.1), 0.3))
    out.add(tick.bm)
    return out
