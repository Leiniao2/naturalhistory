"""
Shared pieces for the brachiopod models (lingulella_chengjiangensis.py, lingula_anatina.py,
mucrospirifer_mucronatus.py): lamp shells, whose two valves are dorsal and ventral (not left
and right as in a clam) and are held on, or anchored by, a fleshy stalk, the pedicle.

  * Lingulid (LingulidSpec, lingulid()): a thin, flattened, tongue-shaped to subtriangular
    organophosphatic shell - a lens of two near-equal valves with a pointed posterior beak,
    painted with concentric growth bands around the beak and a dark line along the
    commissure where the valves meet. A fringe of setae (bristles) sprouts from the margin:
    either a radiating fringe round the front and sides (Lingulella), or three bundles at
    the front margin forming the setal "pseudosiphons" of living Lingula (two inhalant at
    the sides, one exhalant in the middle). The pedicle leaves the beak as a long tube.
    Built in a local frame with the beak at the origin and the shell's long axis +Z, then
    placed with place_lingulid(), which also runs the pedicle from an anchor point on (or
    in) the seabed up to the beak.
  * Spiriferid (SpiriferSpec, spiriferid()): a strophic shell much wider than long, its
    straight hinge line drawn out into pointed ears. Each valve is a fan around the beak
    (polar grid: radial costae follow the grid lines), with a smooth median fold on the
    dorsal valve and a matching sulcus on the ventral one; the anterior commissure arches
    up over the fold (uniplicate) and zig-zags where the costae interlock. Valves are thin
    shells (outer + inner surface), so the dorsal one can be hinged open to show the
    interior, optionally with the paired spiralia (lophophore supports) whose cones point
    out into the ears. A small ventral beak and triangular interarea sit over the hinge.
  * seabed(): a low heightfield patch with optional mounds and burrow pits, skirted down
    to z = 0.

Frames: models face -Y, pivot at the base of the seabed patch (z = 0), Fixed style.
"""

import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh
import nh_tridacna as tc

UP = Vector((0, 0, 1))


# ----------------------------------------------------------------------------- seabed

def seabed(mb, radius, colors, seed=1, bumps=(), pits=(), n_r=14, n_a=56, base=0.03,
           relief=0.012, oval=0.9):
    """Low heightfield patch (top ~base above z = 0) skirted down to z = 0.
      colors: (dark, light) rgb, mottled by noise.
      bumps: [(x, y, radius, height)] gaussian mounds. pits: [(x, y, radius, depth, rgb)]
        burrow openings, sunk into the surface and painted rgb in the middle."""
    sv = Vector((seed * 3.1, seed * 1.7, seed * 0.9))

    def height(x, y):
        h = base + relief * noise.noise(Vector((x, y, 0)) * 6.0 + sv)
        for bx, by, br, bh in bumps:
            h += bh * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (br * br))
        for px, py, pr, pd, _c in pits:
            h -= pd * math.exp(-((x - px) ** 2 + (y - py) ** 2) / (pr * pr))
        return h

    def paint(x, y, z):
        p = Vector((x, y, z))
        m = 0.5 + 0.5 * noise.noise(p * 5.0 + sv)
        c = nh.lerp(colors[0], colors[1], 0.25 + 0.6 * m)
        g = abs(noise.noise(p * 18.0 + sv * 2))
        c = nh.lerp(c, colors[0], nh.smoothstep(0.06, 0.0, g) * 0.4)
        for px, py, pr, _pd, pc in pits:
            d = math.hypot(x - px, y - py) / pr
            c = nh.lerp(c, pc, nh.smoothstep(0.9, 0.35, d))
        return c

    rings, cols = [], []
    rings.append([Vector((0, 0, height(0, 0)))])
    cols.append([paint(0, 0, 0)])
    for i in range(1, n_r + 1):
        rr = radius * (i / n_r)
        row, rc = [], []
        for j in range(n_a):
            a = j / n_a * math.tau
            wob = 1.0 + 0.08 * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 1.5 + sv)
            x, y = math.cos(a) * rr * wob, math.sin(a) * rr * wob * oval
            fade = 1.0 - nh.smoothstep(0.75, 1.0, i / n_r)
            z = base * (1 - fade) * 0.5 + height(x, y) * fade
            row.append(Vector((x, y, z)))
            rc.append(paint(x, y, z))
        rings.append(row)
        cols.append(rc)
    # skirt down to the ground
    rings.append([Vector((p.x * 1.03, p.y * 1.03, 0.0)) for p in rings[-1]])
    cols.append(list(cols[-1]))
    bm = tc.grid(rings, cols, wrap=True)
    tc.orient(bm, lambda f: UP)
    mb.add(bm)
    return height


# ----------------------------------------------------------------------------- lingulids

@dataclass
class LingulidSpec:
    length: float = 0.4          # beak to anterior margin
    width: float = 0.24          # greatest width
    thick: float = 0.035         # half-thickness of the closed shell
    widest: float = 0.6          # position of the greatest width (fraction of the length)
    post_exp: float = 1.5        # outline exponents: low = pointed, high = blunt/truncated
    ant_exp: float = 2.2
    fullness: float = 2.0        # 2 = elliptic sides, higher = parallel-sided
    growth_lines: int = 9
    n_len: int = 22
    n_around: int = 20
    shell: tuple = (0.30, 0.20, 0.12)
    shell_light: tuple = (0.50, 0.36, 0.22)
    margin: tuple = (0.60, 0.50, 0.34)      # thin, paler shell edge
    commissure: tuple = (0.10, 0.07, 0.05)
    setae: str = "fringe"                   # "fringe" or "siphons"
    setae_count: int = 30
    setae_len: float = 0.35                 # fraction of the shell length
    setae_r: float = 0.005
    setae_col: tuple = (0.72, 0.62, 0.42)
    pedicle_r: float = 0.022
    pedicle_col: tuple = (0.62, 0.50, 0.38)
    pedicle_col2: tuple = (0.50, 0.38, 0.28)   # annulation bands
    pedicle_bands: float = 30.0                # bands per unit length (0 = plain)


class Lingulid:
    def __init__(self, s):
        self.s = s
        self.zc = s.length * s.widest

    def half_width(self, z):
        s = self.s
        if z <= 0 or z >= s.length:
            return 0.0
        if z < self.zc:
            d, e = (self.zc - z) / self.zc, s.post_exp
        else:
            d, e = (z - self.zc) / (s.length - self.zc), s.ant_exp
        return s.width * 0.5 * max(0.0, 1.0 - d ** e) ** (1.0 / s.fullness)

    def half_thick(self, z):
        s = self.s
        t = z / s.length
        return s.thick * max(0.0, math.sin(math.pi * min(1.0, t ** 0.8))) ** 0.6

    def growth_stage(self, x, z):
        """k in 0..1: the point lies on the margin of the shell scaled by k about the beak."""
        lo, hi = 1e-3, 1.0
        for _ in range(12):
            k = 0.5 * (lo + hi)
            if abs(x) <= k * self.half_width(z / k) and z <= k * self.s.length:
                hi = k
            else:
                lo = k
        return hi

    def point(self, z, phi):
        w, h = self.half_width(z), self.half_thick(z)
        sp = math.sin(phi)
        return Vector((w * math.cos(phi), h * math.copysign(abs(sp) ** 1.4, sp), z))

    def paint(self, p, sv):
        s = self.s
        k = self.growth_stage(p.x, p.z)
        g = 0.5 + 0.5 * math.cos(k * s.growth_lines * math.tau)
        c = nh.lerp(s.shell, s.shell_light, 0.2 + 0.65 * g ** 4)
        c = nh.lerp(c, s.margin, nh.smoothstep(0.86, 1.0, k))
        n = 0.95 + 0.1 * noise.noise(p * 6.0 / s.length + sv)
        c = tuple(min(1.0, x * n) for x in c)
        # dark line along the commissure (and the slight anterior gape)
        w = self.half_width(p.z)
        if w > 1e-4:
            edge = abs(p.y) / max(self.half_thick(p.z), 1e-4)
            front = nh.smoothstep(0.75, 0.95, p.z / s.length)
            c = nh.lerp(c, s.commissure, nh.smoothstep(0.25 + 0.25 * front, 0.0, edge) * (0.7 + 0.3 * front))
        return c


def lingulid(spec, rng, seed=1):
    """Returns (shell bmesh, setae [(points, radii)], local frame). Beak at origin, axis +Z,
    valves facing +-Y."""
    s = spec
    L = Lingulid(s)
    sv = Vector((seed * 1.3, seed * 2.9, seed * 0.7))
    zs = [s.length * (i / s.n_len) ** 1.0 for i in range(1, s.n_len)]
    phis = [j / s.n_around * math.tau for j in range(s.n_around)]
    rings = [[Vector((0, 0, -0.004))]]
    cols = [[s.shell]]
    for z in zs:
        row = []
        for ph in phis:
            p = L.point(z, ph)
            row.append(p)
        rings.append(row)
        cols.append([L.paint(p, sv) for p in row])
    rings.append([Vector((0, 0, s.length))])
    cols.append([s.margin])
    shell = tc.grid(rings, cols, wrap=True)
    bmesh.ops.recalc_face_normals(shell, faces=shell.faces)

    setae = []
    if s.setae == "fringe":
        # radiating fringe round the front and the front half of the sides
        for i in range(s.setae_count):
            t = i / (s.setae_count - 1)
            side = -1 if t < 0.5 else 1
            q = abs(t - 0.5) * 2               # 0 at the front middle, 1 back at the sides
            z = s.length * (1.0 - 0.55 * q ** 1.3)
            z = min(z, s.length * 0.995)
            w = L.half_width(z)
            base = Vector((side * w * 0.97, 0, z))
            # outward normal of the outline
            dz = 1e-3 * s.length
            dw = L.half_width(min(z + dz, s.length * 0.999)) - L.half_width(max(z - dz, 1e-4))
            nrm = Vector((side * 2 * dz, 0, -dw)).normalized()
            d = (nrm + Vector((0, 0, 0.35 + 0.4 * (1 - q)))).normalized()
            d += Vector((rng.uniform(-0.12, 0.12), rng.uniform(-0.15, 0.15), rng.uniform(-0.08, 0.08)))
            d.normalize()
            ln = s.setae_len * s.length * rng.uniform(0.75, 1.15) * (1.0 - 0.35 * q)
            # soft bristles curve back a little toward the shell's sides
            droop = (Vector((side * 0.6 * q, rng.uniform(-0.15, 0.15), -0.3))) * ln
            pts = [base, base + d * ln * 0.35, base + d * ln * 0.7 + droop * 0.3, base + d * ln + droop]
            setae.append((pts, [s.setae_r, s.setae_r * 0.8, s.setae_r * 0.55, s.setae_r * 0.2]))
    else:
        # three setal pseudosiphons at the front margin: a funnel of bristles each
        for bx in (-0.6, 0.0, 0.6):
            z = s.length * 0.97 if bx == 0 else s.length * 0.93
            w = L.half_width(z)
            centre = Vector((bx * w, 0, z))
            per = max(5, s.setae_count // 3)
            for i in range(per):
                a = i / per * math.tau + rng.uniform(-0.2, 0.2)
                ring = Vector((math.cos(a) * w * 0.22, math.sin(a) * s.thick * 0.6, 0))
                d = (Vector((0, 0, 1)) + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0))
                     + Vector((bx * 0.35, 0, 0))).normalized()
                ln = s.setae_len * s.length * rng.uniform(0.8, 1.1)
                b = centre + ring
                pts = [b, b + d * ln * 0.55, b + d * ln]
                setae.append((pts, [s.setae_r, s.setae_r * 0.8, s.setae_r * 0.3]))
        # short bristles along the front sides
        for side in (-1, 1):
            for i in range(4):
                z = s.length * (0.70 + 0.05 * i)
                w = L.half_width(z)
                b = Vector((side * w * 0.97, 0, z))
                d = Vector((side * 0.8, rng.uniform(-0.2, 0.2), 0.6)).normalized()
                ln = s.setae_len * s.length * 0.4
                setae.append(([b, b + d * ln * 0.5, b + d * ln], [s.setae_r * 0.8, s.setae_r * 0.5, s.setae_r * 0.2]))
    return shell, setae


def frame(axis, face):
    """Rotation taking local +Z to `axis` and local -Y (one valve) toward `face`."""
    z = axis.normalized()
    y = -(face - z * face.dot(z))
    if y.length < 1e-5:
        y = Vector((0, 1, 0)) - z * z.y
    y.normalize()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_4x4()


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append(p0 * a + p1 * b + p2 * c + p3 * d)
    return out


def place_lingulid(mb, spec, rng, beak, axis, face, anchor, anchor_dir=UP, seed=1,
                   pedicle_slack=0.35, wiggle=0.02, holdfast=True, n_ped=14):
    """Builds one lingulid with its beak at `beak`, long axis `axis`, a valve facing `face`,
    and a pedicle from `anchor` (leaving it along anchor_dir) up to the beak."""
    s = spec
    shell, setae = lingulid(spec, rng, seed)
    m = Matrix.Translation(beak) @ frame(axis, face)
    nh.transform(shell, m)
    mb.add(shell)
    for pts, radii in setae:
        mb.add(nh.tube([m @ p for p in pts], radii, sides=3, cap_start=False, cap_end=False), s.setae_col)

    ax = axis.normalized()
    dist = (beak - anchor).length
    p0, p3 = Vector(anchor), Vector(beak) - ax * s.length * 0.02
    p1 = p0 + anchor_dir.normalized() * dist * pedicle_slack
    p2 = p3 - ax * dist * pedicle_slack
    pts = bezier(p0, p1, p2, p3, n_ped)
    ph = rng.uniform(0, math.tau)
    for i, p in enumerate(pts[1:-1], 1):
        t = i / n_ped
        p += Vector((math.sin(t * 9 + ph), math.cos(t * 7 + ph), 0)) * wiggle * math.sin(math.pi * t)
    r = s.pedicle_r
    radii = [r * (1.15 if i == 0 else 1.0 - 0.25 * (i / n_ped)) for i in range(len(pts))]
    ped = nh.tube(pts, radii, sides=7)
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + (a - b).length)

    def pcol(co, n):
        i = min(range(len(pts)), key=lambda k: (pts[k] - co).length_squared)
        if s.pedicle_bands <= 0:
            return s.pedicle_col
        g = 0.5 + 0.5 * math.cos(lengths[i] * s.pedicle_bands * math.tau)
        return nh.lerp(s.pedicle_col, s.pedicle_col2, g * 0.6)

    mb.add(ped, pcol)
    if holdfast:
        hr = r * 2.0
        mb.add(nh.ellipsoid(tuple(p0 + Vector((0, 0, hr * 0.1))), (hr, hr, hr * 0.55), subdivisions=1,
                            deform=lambda n: 1.0 + 0.2 * noise.noise(n * 2.5 + Vector((seed, 0, 0)))),
               s.pedicle_col2)
    return pts


# ----------------------------------------------------------------------------- spiriferids

@dataclass
class SpiriferSpec:
    width: float = 1.0           # hinge width, ear tip to ear tip
    length: float = 0.42         # beak to anterior margin
    body_w: float = 0.62         # width of the rounded body (fraction of the hinge width)
    ear_from: float = 0.95       # fan angle (radians from the midline) where the ears start
    ear_exp: float = 2.4
    dorsal_h: float = 0.08       # dorsal valve convexity
    ventral_h: float = 0.15      # ventral valve convexity
    fold_w: float = 0.20         # half-width of the fold/sulcus (radians of fan angle)
    fold_h: float = 0.05         # extra height of the dorsal fold
    uplift: float = 0.08         # rise of the anterior commissure over the fold
    ribs: int = 13               # costae per flank
    rib_amp: float = 0.012
    growth_lines: int = 14
    thick: float = 0.012
    n_theta: int = 84
    n_r: int = 12
    beak: float = 0.05           # ventral beak overhang behind the hinge
    interarea: float = 0.05      # ventral interarea height
    shell: tuple = (0.70, 0.62, 0.50)
    shell_dark: tuple = (0.50, 0.44, 0.35)
    inside: tuple = (0.33, 0.28, 0.22)
    spiralia_col: tuple = (0.88, 0.84, 0.74)


class Spirifer:
    def __init__(self, s):
        self.s = s
        self.a = s.width * 0.5 * s.body_w
        self.T = math.pi * 0.5

    def rmax(self, th):
        """Beak-to-margin distance along fan angle th (0 = anterior, +-pi/2 = along the hinge)."""
        s = self.s
        dx, dy = math.sin(abs(th)), math.cos(th)
        re = 1.0 / math.sqrt((dx / self.a) ** 2 + (dy / s.length) ** 2)
        k = nh.smoothstep(s.ear_from, self.T, abs(th)) ** s.ear_exp
        return re + (s.width * 0.5 - re) * k

    def fold(self, th):
        return math.exp(-(th / self.s.fold_w) ** 2)

    def rib(self, th):
        s = self.s
        # ribs on the flanks; the fold/sulcus is smooth, bounded by a stronger rib each side
        off = abs(th) - s.fold_w * 1.15
        if off < 0:
            return 0.0
        per = (self.T - s.fold_w * 1.15) / s.ribs
        c = math.cos(off / per * math.tau)
        return c * nh.smoothstep(0.0, per * 0.6, off)

    def ends(self, th):
        return max(0.0, 1.0 - (abs(th) / self.T) ** 3)

    def conv(self, u):
        return (u ** 0.55) * (1.0 - u ** 2.2) ** 0.8 * 1.5

    def z(self, side, u, th):
        """side +1 dorsal (up), -1 ventral (down)."""
        s = self.s
        f = self.fold(th)
        z = s.uplift * f * u ** 2 + s.rib_amp * self.rib(th) * u ** 0.9
        if side > 0:
            z += (s.dorsal_h * self.conv(u) * self.ends(th) + s.fold_h * f * self.conv(u) * 0.8)
        else:
            z -= s.ventral_h * self.conv(u) * self.ends(th) ** 0.8 * (1.0 - 0.45 * f)
            z -= s.interarea * (1 - u) ** 2 * (1 - abs(th) / self.T) * 0.8
        # fine concentric growth lamellae
        z += side * 0.003 * math.cos(u * s.growth_lines * math.tau) * u
        return z

    def point(self, side, u, th, inner=False):
        r = self.rmax(th) * u
        p = Vector((math.sin(th) * r, -math.cos(th) * r, self.z(side, u, th)))
        if inner:
            p.z -= side * self.s.thick * (0.5 + 0.5 * u)
        return p

    def paint(self, side, u, th, p, sv):
        s = self.s
        rb = self.rib(th)
        c = nh.lerp(s.shell_dark, s.shell, 0.55 + 0.45 * rb)
        g = 0.5 + 0.5 * math.cos(u * s.growth_lines * math.tau)
        c = nh.lerp(c, s.shell_dark, 0.25 * g ** 4)
        c = nh.lerp(c, nh.lerp(s.shell, (1, 1, 1), 0.2), self.fold(th) * 0.35 * u)
        n = 0.88 + 0.24 * noise.noise(p * 6.0 + sv)
        return tuple(min(1.0, x * n) for x in c)


def spiriferid(spec, seed=1, gape=math.radians(4), spiralia=False):
    """One spiriferid shell (list of (bmesh, color-or-None)), ventral valve down, beak at the
    origin, hinge along X, anterior toward -Y. gape: dorsal valve opening angle."""
    s = spec
    S = Spirifer(s)
    sv = Vector((seed * 2.3, seed * 0.7, seed * 1.9))
    T = S.T
    ths = [-T + 2 * T * i / (s.n_theta - 1) for i in range(s.n_theta)]
    us = [(i / s.n_r) ** 0.9 for i in range(1, s.n_r + 1)]
    parts = []
    hinge_rot = Matrix.Rotation(-gape, 4, "X")
    for side in (1, -1):
        rings, cols = [[Vector((0, 0, 0))]], [[s.shell_dark]]
        for u in us:
            row = [S.point(side, u, th) for th in ths]
            rings.append(row)
            cols.append([S.paint(side, u, th, p, sv) for th, p in zip(ths, row)])
        rim = [S.point(side, 1.0, th, inner=True) for th in ths]
        rings.append(rim)
        cols.append([nh.lerp(s.shell_dark, s.inside, 0.6)] * len(ths))
        for u in reversed(us[:-1:3]):
            rings.append([S.point(side, u, th, inner=True) for th in ths])
            cols.append([s.inside] * len(ths))
        rings.append([Vector((0, 0, -side * s.thick))])
        cols.append([s.inside])
        v = tc.grid(rings, cols)
        bmesh.ops.recalc_face_normals(v, faces=v.faces)
        if side > 0 and gape:
            nh.transform(v, hinge_rot)
        parts.append((v, None))

    # ventral beak and interarea over the hinge: a low triangle with a dark delthyrium
    iw = S.a * 0.85
    apex = Vector((0, s.beak, -s.interarea * 0.9))
    rows, cols = [], []
    for k in range(5):
        t = k / 4
        x = -iw + 2 * iw * t
        rows.append(Vector((x, 0.0, -0.004)))
    rings = [rows, [apex.lerp(p, 0.15) for p in rows], [apex]]
    ccol = [[s.shell_dark] * 5, [s.shell_dark] * 5, [s.shell_dark]]
    tri = tc.grid(rings, ccol)
    tc.orient(tri, lambda f: Vector((0, 1, 0.3)))
    parts.append((tri, None))
    beakbm = nh.ellipsoid(tuple(apex + Vector((0, -0.02, 0.012))), (0.04, 0.045, 0.028), subdivisions=2)
    parts.append((beakbm, s.shell_dark))
    # delthyrium (triangular notch in the interarea, closed by the pedicle)
    d = tc.grid([[Vector((-0.03, 0.003, -0.002)), Vector((0.03, 0.003, -0.002))], [apex + Vector((0, 0.004, 0.0))]],
                [[s.inside] * 2, [s.inside]])
    tc.orient(d, lambda f: Vector((0, 1, 0.3)))
    parts.append((d, None))

    if spiralia:
        # paired spiral cones in the body cavity, apices pointing out into the ears
        for sx in (-1, 1):
            n_turns, per_turn = 7, 14
            pts, radii = [], []
            for i in range(n_turns * per_turn + 1):
                t = i / (n_turns * per_turn)
                x = sx * (0.04 + t * S.a * 0.85)
                th = math.atan2(abs(x), S.s.length * 0.35) * sx
                u = min(0.9, abs(x) / max(S.rmax(th), 1e-3) + 0.05)
                ytop = S.point(1, u, th, inner=True)
                ybot = S.point(-1, u, th, inner=True)
                ytop = hinge_rot @ ytop
                cy, cz = -s.length * 0.33, (ytop.z + ybot.z) * 0.5
                half = max(0.005, (ytop.z - ybot.z) * 0.5) * 0.75
                rad = half * (1.0 - t) ** 0.9 + 0.004
                a = t * n_turns * math.tau
                pts.append(Vector((x, cy + math.cos(a) * rad * 1.4, cz + math.sin(a) * rad)))
                radii.append(0.0045)
            parts.append((nh.tube(pts, radii, sides=4, cap_start=False, cap_end=False), s.spiralia_col))
    return parts


def place(mb, parts, matrix):
    for bm, col in parts:
        nh.transform(bm, matrix)
        mb.add(bm, col) if col is not None else mb.add(bm)


def finish(mb, name, roughness=0.6, floor=0.0):
    obj = mb.to_object(name, roughness=roughness)
    for v in obj.data.vertices:
        v.co.z = max(v.co.z, floor)
    nh.ground_to_zero(obj)
    return obj


VIEWS = ((30, 28), (5, 70), (-90, 8))
