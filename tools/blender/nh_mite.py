"""
Shared builder for the mite models (dermatophagoides_farinae.py, demodex_folliculorum.py,
otodectes_cynotis.py, tetranychus_urticae.py, phytoseiulus_persimilis.py).

A mite (Acari) has no separate head or waist: the body is one sac, the idiosoma, with a small
mouthpart capsule, the gnathosoma, in front carrying a pair of chelicerae (jaws or piercing
stylets) and a pair of jointed palps. Four pairs of short jointed legs come from the front half of
the body; most mites carry a few long bristles (setae).

  * Body: the idiosoma as one lofted shell around the Y axis, its width/height profile given
    per species (plump oval, pear, worm-like), flatter on the belly, with an optional
    displacement (striae, annuli) applied along the normals.
  * gnathosoma(): capitulum, chelicerae and palps in front of the body.
  * leg(): a jointed leg - podomeres that narrow at every joint - arching up from the flank and
    coming down to the ground (walkers), or a short telescoped stump (follicle mites); tips are
    claws(), a stalked sucker() (pretarsus) or long terminal setae.
  * seta(): a fine tapering bristle growing out of the body surface.
  * build(spec): the whole mite from a Spec, in its own frame (faces -Y, Z up, feet at z = 0),
    into a MeshBuilder; place() moves a finished mite onto a scene (e.g. a leaf_patch()).
"""

import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh

UP = Vector((0, 0, 1))


# ---------------------------------------------------------------- body

def oval(width, height, front=2.0, rear=2.0, dz=None):
    """Superellipse profile: (half-width, half-height, z offset) at t in [-1 front, 1 rear].
    front/rear: exponents (2 = elliptical end, higher = blunter, lower = more pointed).
    dz(t): optional midline height offset (e.g. a humped back)."""
    def f(t):
        p = front if t < 0 else rear
        k = max(0.0, 1.0 - abs(t) ** p) ** (1.0 / p)
        return width * k, height * k, dz(t) if dz else 0.0
    return f


class Body:
    """Idiosoma lofted around the Y axis: profile(t) -> (half_width, half_height, z_offset)."""

    def __init__(self, half_len, profile, center_z=0.0, belly=0.6, deform=None):
        self.L = half_len
        self.profile = profile
        self.cz = center_z
        self.belly = belly          # underside flattened to this fraction of the half-height
        self.deform = deform        # fn(co, n) -> offset along the normal

    def point(self, t, phi):
        """Surface point at t (-1 front .. 1 rear) and angle phi around the axis (0 = +X side,
        pi/2 = top, -pi/2 = belly)."""
        t = max(-1.0, min(1.0, t))
        w, h, dz = self.profile(t)
        s = math.sin(phi)
        if s < 0:
            s *= self.belly
        return Vector((w * math.cos(phi), t * self.L, self.cz + dz + h * s))

    def normal(self, t, phi):
        e = 0.01
        dt = self.point(min(t + e, 0.999), phi) - self.point(max(t - e, -0.999), phi)
        dp = self.point(t, phi + e) - self.point(t, phi - e)
        n = dt.cross(dp).normalized()
        p = self.point(t, phi)
        if n.dot(p - Vector((0, p.y, self.cz))) < 0:
            n = -n
        return n

    def mesh(self, nu=24, nv=24, even=0.0):
        """nu points around, nv rings along; even: 0 = rings bunched at the rounded ends,
        1 = evenly spaced (long bodies with fine annuli)."""
        bm = bmesh.new()
        rings = []
        for k in range(1, nv):
            t = -math.cos(math.pi * k / nv) * (1.0 - even) + (2.0 * k / nv - 1.0) * even
            rings.append([bm.verts.new(self.point(t, i / nu * math.tau)) for i in range(nu)])
        front = bm.verts.new(self.point(-1.0, 0.0))
        rear = bm.verts.new(self.point(1.0, 0.0))
        for a, b in zip(rings, rings[1:]):
            for i in range(nu):
                j = (i + 1) % nu
                bm.faces.new([a[i], a[j], b[j], b[i]])
        for i in range(nu):
            j = (i + 1) % nu
            bm.faces.new([front, rings[0][j], rings[0][i]])
            bm.faces.new([rear, rings[-1][i], rings[-1][j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if self.deform:
            bm.normal_update()
            offs = [(v, self.deform(v.co.copy(), v.normal.copy())) for v in bm.verts]
            for v, d in offs:
                v.co += v.normal * d
        return bm


# ---------------------------------------------------------------- appendages

def seta(p, direction, length, radius=0.006, bend=None, sides=3):
    """Fine bristle from p along direction, tapering to a point; bend: vector added to the
    second half so long setae arch (e.g. backwards / downwards)."""
    d = direction.normalized()
    mid = p + d * length * 0.5
    tip = p + d * length
    if bend is not None:
        mid += bend * length * 0.15
        tip += bend * length * 0.45
    return nh.tube([p - d * radius, mid, tip], [radius, radius * 0.6, 0.0], sides=sides)


def claws(tip, axis, size=0.02, n=2, color_sides=3):
    """n small hooked claws fanned sideways at a leg tip."""
    out = []
    ax = axis.normalized()
    lat = ax.cross(UP)
    lat = lat.normalized() if lat.length > 1e-4 else Vector((1, 0, 0))
    down = ax.cross(lat).normalized()
    if down.z > 0:
        down = -down
    for k in range(n):
        a = (k - (n - 1) / 2) * 0.9
        spread = (ax * math.cos(a) + lat * math.sin(a)).normalized()
        p0 = tip - ax * size * 0.3
        p1 = tip + spread * size * 0.8
        p2 = p1 + spread * size * 0.35 + down * size * 0.6
        out.append(nh.tube([p0, p1, p2], [size * 0.22, size * 0.16, 0.0], sides=color_sides))
    return out


def sucker(tip, axis, stalk=0.08, radius=0.008, disc=0.035, sides=8):
    """Stalked sucker (pretarsus): a thin unjointed pedicel then a bell-shaped disc whose mouth
    faces forward-down onto the ground."""
    ax = axis.normalized()
    s0 = tip - ax * radius
    s1 = tip + ax * stalk * 0.85
    bell_dir = (ax * 0.6 - UP * 0.8).normalized()
    b0 = s1 + bell_dir * disc * 0.15
    b1 = s1 + bell_dir * disc * 0.65
    return nh.tube([s0, s1, b0, b1], [radius, radius * 0.9, radius * 1.4, disc], sides=sides,
                   cap_end=True)


@dataclass
class Leg:
    """One leg (mirrored to both sides). angle: degrees from straight out sideways, positive
    swings the leg forward (-Y). lift: knee height above the hip as a fraction of length."""
    t: float                       # attachment along the body (-1 front .. 1 rear)
    length: float
    angle: float
    lift: float = 0.35
    phi: float = -0.35             # attachment angle around the body (negative = below the flank)
    radius: float = 0.03
    taper: float = 0.5             # radius lost from hip to tip (fraction)
    segments: int = 5              # podomeres after the coxa
    tip: str = "claw"              # claw | sucker | setae | none
    tip_size: float = 0.03
    stalk: float = 0.08            # sucker pedicel length
    stub: bool = False             # short stump angled down-out (no ground contact)
    dip: float = 40.0              # stub: degrees below horizontal
    foot_z: float = 0.0
    sides: int = 6


def leg(body, spec: Leg, side):
    """Returns (shell, joints, tip point, tip axis)."""
    s = 1 if side > 0 else -1
    hip = body.point(spec.t, math.pi - spec.phi if s < 0 else spec.phi)
    a = math.radians(spec.angle)
    out = Vector((s * math.cos(a), -math.sin(a), 0.0))
    L = spec.length
    n = spec.segments
    if spec.stub:
        d = math.radians(spec.dip)
        dirv = (out * math.cos(d) - UP * math.sin(d)).normalized()
        joints = [hip - dirv * spec.radius * 0.6]
        for i in range(1, n + 1):
            f = i / n
            joints.append(hip + dirv * L * f + UP * 0.08 * L * math.sin(math.pi * f))
    else:
        knee = hip.z + spec.lift * L
        fz = spec.foot_z
        # horizontal reach and height at each joint, coxa .. tarsus tip
        prof = [(0.0, hip.z), (0.14, hip.z + 0.55 * (knee - hip.z)), (0.40, knee),
                (0.64, knee - 0.35 * (knee - fz)), (0.84, fz + 0.12 * (knee - fz)), (1.0, fz)]
        if n != 5:
            # resample to n + 1 joints along the same curve
            res = []
            for i in range(n + 1):
                u = i / n * (len(prof) - 1)
                k = min(int(u), len(prof) - 2)
                f = u - k
                res.append((prof[k][0] + (prof[k + 1][0] - prof[k][0]) * f,
                            prof[k][1] + (prof[k + 1][1] - prof[k][1]) * f))
            prof = res
        joints = [Vector((hip.x, hip.y, 0)) + out * (r * L) + UP * z for r, z in prof]
        joints[0] -= out * spec.radius * 0.6
    pts, radii = [], []
    for i in range(n):
        r = spec.radius * (1.0 - spec.taper * i / n)
        pts += [joints[i], joints[i].lerp(joints[i + 1], 0.45)]
        radii += [r * 0.74, r]
    pts.append(joints[-1])
    radii.append(spec.radius * (1.0 - spec.taper) * 0.65)
    shell = nh.tube(pts, radii, sides=spec.sides)
    axis = (joints[-1] - joints[-2]).normalized()
    return shell, joints, joints[-1], axis


def joint_color(joints, base, dark, ring=0.012, amount=0.6):
    """Leg colour fn with darker rings at the joints (and a slightly paler underside)."""
    def color(co, n):
        d = min((co - j).length for j in joints[1:-1]) if len(joints) > 2 else 1.0
        c = nh.lerp(base, dark, amount * math.exp(-(d / ring) ** 2))
        return c
    return color


def gnathosoma(front, size, base, chelicera, palp, chel_len=1.0, palp_len=1.0, palp_spread=1.0,
               down=0.15):
    """Mouthparts in front of the body: capitulum + chelicerae + palps. Returns [(shell, colour)]."""
    s = size
    f = Vector(front)
    c = f + Vector((0, -0.32 * s, -down * s))
    out = [(nh.uv_ellipsoid(c, (0.42 * s, 0.6 * s, 0.32 * s), segments=12, rings=7), base)]
    for x in (-1, 1):
        p0 = c + Vector((x * 0.13 * s, 0.0, 0.08 * s))
        p1 = p0 + Vector((0, -0.55 * s * chel_len, -0.02 * s))
        p2 = p1 + Vector((0, -0.28 * s * chel_len, -0.08 * s))
        out.append((nh.tube([p0, p1, p2], [0.12 * s, 0.10 * s, 0.03 * s], sides=6), chelicera))
        q0 = c + Vector((x * 0.30 * s, 0.05 * s, -0.04 * s))
        q1 = q0 + Vector((x * 0.16 * s * palp_spread, -0.30 * s * palp_len, 0.04 * s))
        q2 = q1 + Vector((x * 0.08 * s * palp_spread, -0.30 * s * palp_len, -0.03 * s))
        q3 = q2 + Vector((-x * 0.02 * s, -0.22 * s * palp_len, -0.08 * s))
        out.append((nh.tube([q0, q1, q1.lerp(q2, 0.5), q2, q3],
                            [0.10 * s, 0.075 * s, 0.085 * s, 0.065 * s, 0.035 * s], sides=6), palp))
    return out


# ---------------------------------------------------------------- whole mite

@dataclass
class Spec:
    body: Body
    body_color: Callable
    legs: List[Leg]
    leg_color: tuple = (0.8, 0.7, 0.6)
    leg_joint: tuple = (0.6, 0.5, 0.4)
    claw_color: tuple = (0.35, 0.25, 0.15)
    body_res: tuple = (24, 24)               # (around, along[, even]) - see Body.mesh
    gnatho_size: float = 0.15
    gnatho_colors: tuple = ((0.8, 0.7, 0.6), (0.6, 0.45, 0.35), (0.75, 0.65, 0.55))
    gnatho_kw: dict = field(default_factory=dict)
    # setae: (t, phi, length, direction or None (= surface normal), bend or None), mirrored if phi
    # is not on the midline
    setae: list = field(default_factory=list)
    seta_color: tuple = (0.9, 0.9, 0.85)
    seta_radius: float = 0.006
    tip_setae: float = 0.0                   # length of the paired terminal setae on "setae" tips
    roughness: float = 0.5


def build(spec: Spec, mb: Optional[nh.MeshBuilder] = None):
    """Builds the mite into mb (or a new MeshBuilder). Returns (mb, info) with info["hip_z"]
    (mean leg attachment height) and info["tips"] [(tip, axis)]."""
    mb = mb or nh.MeshBuilder()
    body = spec.body
    mb.add(body.mesh(*spec.body_res), spec.body_color)
    g = spec.gnatho_colors
    for shell, col in gnathosoma(body.point(-1.0, 0.0), spec.gnatho_size, g[0], g[1], g[2],
                                 **spec.gnatho_kw):
        mb.add(shell, col)
    tips, hips = [], []
    for lg in spec.legs:
        for side in (-1, 1):
            shell, joints, tip, axis = leg(body, lg, side)
            mb.add(shell, joint_color(joints, spec.leg_color, spec.leg_joint,
                                      ring=lg.radius * 0.5))
            hips.append(joints[0].z)
            tips.append((tip, axis))
            if lg.tip == "claw":
                for c in claws(tip, axis, lg.tip_size):
                    mb.add(c, spec.claw_color, smooth=False)
            elif lg.tip == "sucker":
                mb.add(sucker(tip, axis, stalk=lg.stalk, radius=lg.radius * 0.3, disc=lg.tip_size),
                       spec.leg_color)
            elif lg.tip == "setae":
                for k in (-1, 1):
                    d = (axis + Vector((0, 0, 0.25)) + axis.cross(UP).normalized() * 0.18 * k)
                    mb.add(seta(tip, d, spec.tip_setae, spec.seta_radius * 1.1,
                                bend=Vector((0, 0, -0.4))), spec.seta_color)
    for t, phi, length, direction, bend in spec.setae:
        phis = [phi] if abs(math.cos(phi)) < 1e-3 else [phi, math.pi - phi]
        for ph in phis:
            p = body.point(t, ph)
            nrm = body.normal(t, ph)
            if direction is None:
                d = nrm
            else:
                d = Vector(direction)
                if ph != phi:
                    d.x = -d.x
            mb.add(seta(p - nrm * 0.004, d, length, spec.seta_radius, bend=bend), spec.seta_color)
    return mb, {"hip_z": sum(hips) / len(hips), "tips": tips}


def place(src: nh.MeshBuilder, dst: nh.MeshBuilder, loc=(0, 0, 0), yaw=0.0, scale=1.0):
    """Moves everything in src (a finished mite) by scale, yaw (degrees about Z) and loc into dst."""
    m = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ \
        Matrix.Scale(scale, 4)
    nh.transform(src.bm, m)
    dst.add(src.bm)


def glossy(base, dark, gloss, light_dir=Vector((-0.45, -0.55, 0.70)).normalized(), power=16,
           amount=0.8):
    """Diffuse map shader: bake a soft shine into the vertex colour (top-lit, dark underside)."""
    def color(co, n):
        c = nh.lerp(dark, base, nh.smoothstep(-0.6, 0.4, n.z))
        h = max(0.0, n.dot(light_dir)) ** power
        return nh.lerp(c, gloss, h * amount)
    return color


# ---------------------------------------------------------------- leaf patch

@dataclass
class Leaf:
    length: float = 1.6
    half_width: float = 0.55
    curl: float = 0.06               # edges lift by this much
    green: tuple = (0.24, 0.50, 0.13)
    light: tuple = (0.40, 0.64, 0.20)
    edge: tuple = (0.17, 0.38, 0.09)
    vein: tuple = (0.52, 0.72, 0.30)
    stipple: Optional[Callable] = None   # fn(co) -> 0..1 pale feeding-damage speckle amount
    stipple_color: tuple = (0.78, 0.80, 0.45)

    def width(self, v):
        return self.half_width * math.sin(math.pi * min(v * 1.02, 1.0)) ** 0.65 * (1.0 - 0.3 * v) + 0.01

    def point(self, u, v):
        """u in [-1, 1] across, v in [0, 1] from stalk to tip."""
        w = self.width(v)
        x, y = u * w, -self.length * 0.5 + v * self.length
        z = self.curl * abs(u) ** 3 + 0.05 * max(0.0, v - 0.8) ** 2 * 10
        z -= 0.008 * (1.0 - abs(u)) ** 3
        z += 0.006 * noise.noise(Vector((x * 5, y * 5, 0.7)))
        return Vector((x, y, z))

    def height(self, x, y):
        v = min(1.0, max(0.0, (y + self.length * 0.5) / self.length))
        return self.point(max(-1.0, min(1.0, x / self.width(v))), v).z


def leaf_patch(mb, leaf: Leaf, nu=12, nv=20, side_veins=5):
    """Ovate leaf lying on the ground (top side up) with a raised midrib, side veins and a stalk."""
    bm = bmesh.new()
    top = [[bm.verts.new(leaf.point(-1 + 2 * i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    bot = [[bm.verts.new(leaf.point(-1 + 2 * i / nu, j / nv) - Vector((0, 0, 0.014))) for i in range(nu + 1)]
           for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
    for j in range(nv):
        bm.faces.new([top[j][0], bot[j][0], bot[j + 1][0], top[j + 1][0]])
        bm.faces.new([top[j][nu], top[j + 1][nu], bot[j + 1][nu], bot[j][nu]])

    def color(co, n):
        v = (co.y + leaf.length * 0.5) / leaf.length
        u = min(1.0, abs(co.x) / leaf.width(max(0.0, min(1.0, v))))
        c = nh.lerp(leaf.light, leaf.green, nh.smoothstep(0.0, 0.5, u))
        c = nh.lerp(c, leaf.edge, nh.smoothstep(0.8, 1.0, u))
        if n.z < -0.3:
            return nh.lerp(c, leaf.edge, 0.5)
        if leaf.stipple:
            c = nh.lerp(c, leaf.stipple_color, leaf.stipple(co))
        return c
    mb.add(bm, color)

    lift = Vector((0, 0, 0.005))
    mid = [leaf.point(0, v) + lift for v in (0.0, 0.2, 0.4, 0.6, 0.8, 0.97)]
    mb.add(nh.tube(mid, [0.014, 0.012, 0.010, 0.008, 0.005, 0.0], sides=5), leaf.vein)
    for k in range(side_veins):
        v0 = 0.12 + k * 0.15
        for s in (-1, 1):
            pts = [leaf.point(s * u, v0 + u * 0.14) + lift for u in (0.0, 0.35, 0.65, 0.9)]
            mb.add(nh.tube(pts, [0.007, 0.0055, 0.004, 0.0], sides=4), leaf.vein)
    base = leaf.point(0, 0)
    mb.add(nh.tube([base, base + Vector((0.01, -0.09, -0.008)), base + Vector((0.03, -0.17, -0.004))],
                   [0.016, 0.014, 0.012], sides=6), leaf.green)
