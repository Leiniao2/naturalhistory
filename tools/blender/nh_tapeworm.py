"""
Shared pieces for the tapeworm models (taenia_solium.py, taenia_saginata.py,
echinococcus_granulosus.py, spirometra_mansoni.py).

  * chain(): the strobila as a list of proglottids, each (length, width, stage), growing
    from tiny immature ones behind the neck through squarish mature ones to the big
    gravid ones at the end (stage 0 = immature, 1 = mature, 2 = gravid, fractional in
    between).
  * Paths: the worm's midline as an evenly sampled polyline. spiral_path() coils the
    ribbon outwards from the scolex (the turns spread as the ribbon widens, so they never
    touch), meander_path() folds it back and forth in loops, curve_path() follows control
    points. A real worm is metres long; coiling or folding it keeps the model compact so it
    reads at map scale. The front end (neck and scolex) can lift off the coil.
  * strobila(): the flat ribbon swept along the path, proglottid by proglottid. Each
    proglottid is narrower at its front than at its back, so the margins have the typical
    saw-tooth outline and the boundaries show as shadowed grooves; the caller paints each
    proglottid (uterus, genital pore...) through a colour function of (proglottid, u, v).
  * scolex_*(): the holdfast - a knob with four cup-shaped suckers and optionally a
    rostellum with a double crown of hooks (Taenia solium, Echinococcus), or an elongate,
    spoon-shaped scolex with two slit-like bothria (Spirometra).

Frame: the coil lies in the XY plane (flat ribbon, thickness along Z); pivot at the
bounding-box centre (Drift style).
"""

import math

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh

IVORY = (0.93, 0.90, 0.80)       # immature proglottids, neck: pale, slightly translucent
CREAM = (0.95, 0.90, 0.74)       # mature
GRAVID = (0.92, 0.84, 0.62)      # gravid: warmer, egg-filled
UTERUS = (0.78, 0.66, 0.42)      # egg-filled uterus showing through
SUCKER = (0.86, 0.80, 0.66)
SUCKER_CUP = (0.42, 0.34, 0.24)
HOOK = (0.62, 0.44, 0.16)        # amber hooks
GROOVE_SHADE = 0.80              # colour factor of the groove at each proglottid's front edge


# ---------------------------------------------------------------- proglottid chain

def chain(n, start, mature, gravid, mature_at=0.35, gravid_at=0.65, end_shrink=0.0):
    """n proglottids as [(length, width, stage)]. start/mature/gravid: (length, width) of the
    first one, the first mature one (at fraction mature_at along the chain) and the first
    gravid one (gravid_at); beyond that they stay gravid, narrowing by end_shrink at the end."""
    out = []
    for i in range(n):
        f = i / max(n - 1, 1)
        if f < mature_at:
            k = (f / mature_at) ** 0.8
            lw = nh.lerp(start, mature, k)
            stage = k
        elif f < gravid_at:
            k = (f - mature_at) / (gravid_at - mature_at)
            lw = nh.lerp(mature, gravid, nh.smoothstep(0.0, 1.0, k))
            stage = 1.0 + k
        else:
            k = (f - gravid_at) / max(1.0 - gravid_at, 1e-6)
            lw = (gravid[0], gravid[1] * (1.0 - end_shrink * k))
            stage = 2.0
        out.append((lw[0], lw[1], stage))
    return out


# ---------------------------------------------------------------- paths

class Path:
    """Polyline with arc-length lookup."""

    def __init__(self, pts):
        self.pts = [Vector(p) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def at(self, s):
        """(point, unit tangent) at arc length s."""
        s = min(max(s, 0.0), self.length)
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        a, b = self.pts[lo], self.pts[hi]
        seg = self.cum[hi] - self.cum[lo] or 1.0
        p = a.lerp(b, (s - self.cum[lo]) / seg)
        i0, i1 = max(lo - 1, 0), min(hi + 1, len(self.pts) - 1)
        t = (self.pts[i1] - self.pts[i0]).normalized()
        return p, t


def width_lookup(progs, neck_len, neck_width):
    """Width of the ribbon at arc length s (from the scolex)."""
    starts, s = [], neck_len
    for l, w, _ in progs:
        starts.append(s)
        s += l

    def width(x):
        if x < neck_len:
            return neck_width
        lo, hi = 0, len(starts) - 1
        while hi > lo:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= x:
                lo = mid
            else:
                hi = mid - 1
        return progs[lo][1]
    return width, s


def spiral_path(length, width_at, r0=0.06, gap=0.012, step=0.006, aspect=1.0, wobble=0.0,
                seed=0.0):
    """Coil outwards from radius r0; the spacing between turns follows the ribbon width at
    each point so neighbouring turns never touch. aspect > 1 stretches the coil along X.
    wobble: radial waviness (fraction of the local width) so it isn't machine-perfect."""
    pts = []
    th, r, s = 0.0, r0, 0.0
    while s < length + 0.1:
        w = width_at(s)
        wob = wobble * w * noise.noise(Vector((th * 0.6, seed, 0.0)))
        pts.append(Vector((math.cos(th) * (r + wob) * aspect, math.sin(th) * (r + wob), 0.0)))
        dr = (w + gap) / math.tau
        dth = step / math.hypot(r * max(aspect, 1.0), dr)
        th += dth
        r += dr * dth
        s += step
    return pts


def meander_path(length, width_at, lane=1.4, gap=0.02, step=0.008, wiggle=0.04, seed=0.0):
    """Folds the ribbon back and forth in lanes along X, each U-turn sized to the ribbon
    width, the lanes slightly wavy and uneven."""
    pts = []
    y, d, s, lane_i = 0.0, 1, 0.0, 0
    while s < length + 0.1:
        ln = lane * (1.0 + 0.12 * noise.noise(Vector((lane_i * 1.7, seed, 0.3))))
        x0 = -d * ln / 2
        n = max(2, int(ln / step))
        for k in range(n):
            x = x0 + d * ln * k / n
            yy = y + wiggle * math.sin(x * 4.0 + lane_i * 1.3) * math.sin(math.pi * k / n)
            pts.append(Vector((x, yy, 0.0)))
        s += ln
        w = max(width_at(s), width_at(s + ln))
        rr = (w + gap) / 2
        cx = x0 + d * ln
        m = max(4, int(math.pi * rr / step))
        for k in range(m):
            a = -math.pi / 2 + math.pi * k / m
            pts.append(Vector((cx + d * rr * math.cos(a), y + rr + rr * math.sin(a), 0.0)))
        s += math.pi * rr
        y += 2 * rr
        d = -d
        lane_i += 1
    return pts


def tangle_path(length, width_at, radius=0.6, curl=0.25, bias=0.12, steer=8.0, step=0.008,
                seed=0.0, start=(0.0, 0.0), heading=0.0):
    """A wandering, looping midline that stays inside a disc of `radius`. The heading turns
    by a smoothly varying curvature scaled to the local ribbon width (curl and bias are
    curvature x width: loops of a few widths/curl across, mostly turning one way), and
    bends back towards the centre whenever the path strays outside. Pass it through
    drape() so crossing strands lie on top of each other instead of intersecting."""
    pts = []
    p = Vector((start[0], start[1], 0.0))
    h = heading
    s = 0.0
    while s < length + 0.1:
        pts.append(p.copy())
        w = max(width_at(s), 0.02)
        k = (curl * noise.noise(Vector((s * 2.0, seed, 0.5))) + bias) / w
        d = p.length
        if d > radius * 0.6:
            to_c = math.atan2(-p.y, -p.x)
            err = math.atan2(math.sin(to_c - h), math.cos(to_c - h))
            k += steer * err * nh.smoothstep(radius * 0.6, radius, d)
        h += k * step
        p += Vector((math.cos(h), math.sin(h), 0.0)) * step
        s += step
    return pts


def warp(pts, amount=0.15, freq=1.6, seed=0.0):
    """Bends the whole layout with a smooth displacement field, so a regular coil turns into
    an irregular, organic one while neighbouring turns move together (keeping their spacing)."""
    off = Vector((seed * 0.31 + 0.5, seed * 0.17 + 0.25, 0.37))
    out = []
    for p in pts:
        d = noise.noise_vector(Vector((p.x, p.y, 0.0)) * freq + off)
        out.append(Vector((p.x + d.x * amount, p.y + d.y * amount, p.z)))
    return out


def drape(pts, width_at, thick_at, clearance=0.004, slope=0.35, passes=3):
    """Lifts later parts of the ribbon over earlier ones wherever they cross (in path order:
    the tail end ends up on top), ramping up and down gently either side of each crossing."""
    path = Path(pts)
    n = len(path.pts)
    xy = [Vector((p.x, p.y)) for p in path.pts]
    ws = [width_at(s) for s in path.cum]
    ths = [thick_at(s) for s in path.cum]
    base = [p.z for p in path.pts]
    z = list(base)
    cell = max(ws) * 1.1
    for _ in range(passes):
        grid = {}
        for i in range(n):
            key = (int(math.floor(xy[i].x / cell)), int(math.floor(xy[i].y / cell)))
            need = base[i]
            for gx in (key[0] - 1, key[0], key[0] + 1):
                for gy in (key[1] - 1, key[1], key[1] + 1):
                    for j in grid.get((gx, gy), ()):
                        if path.cum[i] - path.cum[j] < (ws[i] + ws[j]) * 1.2:
                            continue
                        if (xy[i] - xy[j]).length < (ws[i] + ws[j]) * 0.5 + 0.004:
                            need = max(need, z[j] + (ths[i] + ths[j]) * 0.5 + clearance)
            z[i] = max(z[i], need)
            grid.setdefault(key, []).append(i)
        # slope-limit so the ribbon ramps over crossings instead of stepping
        for i in range(1, n):
            z[i] = max(z[i], z[i - 1] - slope * (path.cum[i] - path.cum[i - 1]))
        for i in range(n - 2, -1, -1):
            z[i] = max(z[i], z[i + 1] - slope * (path.cum[i + 1] - path.cum[i]))
    return [Vector((p.x, p.y, zz)) for p, zz in zip(path.pts, z)]


def catmull_rom(ctrl, per_span=30):
    pts = []
    c = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    for i in range(1, len(c) - 2):
        p0, p1, p2, p3 = c[i - 1], c[i], c[i + 1], c[i + 2]
        for k in range(per_span):
            t = k / per_span
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(ctrl[-1])
    return pts


def lift_front(pts, height, over, heap=0.0):
    """Raises the front of the path (the neck and scolex rear up off the coil) and optionally
    heaps the coil a little (the inner turns sit higher)."""
    path = Path(pts)
    out = []
    for p, s in zip(path.pts, path.cum):
        k = 1.0 - nh.smoothstep(0.0, over, s)
        z = height * k * k * (3 - 2 * k) + heap * (1.0 - s / path.length)
        out.append(Vector((p.x, p.y, p.z + z)))
    return out


# ---------------------------------------------------------------- the ribbon

def _section(sides, squareness):
    """Unit cross-section (x across, z up): a flattened superellipse, a vertex on the
    midline at top and bottom (for uterus / rosette paint)."""
    pts = []
    for k in range(sides):
        a = k / sides * math.tau
        c, s = math.cos(a), math.sin(a)
        pts.append((math.copysign(abs(c) ** squareness, c), math.copysign(abs(s) ** squareness, s)))
    return pts


def strobila(path, progs, neck_len, neck_width, paint, thickness=0.14, min_thickness=0.008,
             rings=(0.0, 0.94), gravid_rings=None, front_narrow=0.84, sides=8, squareness=0.55,
             bank=0.0, neck_rings=8, round_end=True, section=None, stage_rings=None,
             width_profile=None):
    """Sweeps the ribbon along `path` (arc length 0 = the scolex end).
      progs: from chain(); thickness: ribbon thickness / width
      rings: positions (fractions of a proglottid's length) of the cross-sections in each
        proglottid; gravid_rings optionally more for the gravid ones
      front_narrow: width of a proglottid's front edge relative to its back edge
      paint(i, prog, u, v, top) -> rgb: u along the proglottid (0..1), v across (-1..1),
        top = +1 on the upper face, -1 below
      bank: amplitude (radians) of a slow twist of the ribbon about its midline
      section: optional custom unit cross-section [(x, z)] instead of the superellipse
      stage_rings: optional fn(stage) -> ring positions, overriding rings / gravid_rings
      width_profile: optional fn(stage, u) -> width factor, overriding front_narrow
    Returns a bmesh with its own "Col" layer (add it with color=None)."""
    sec = section or _section(sides, squareness)
    stations = []  # (s, width, thickness, colour fn(v, top))

    def neck_col(v, top, s):
        return IVORY
    for k in range(neck_rings):
        s = neck_len * k / neck_rings
        w = neck_width * (0.9 + 0.1 * k / neck_rings)
        stations.append((s, w, max(w * thickness * 1.6, min_thickness), lambda v, t, s=s: IVORY))
    s0 = neck_len
    for i, (l, w, stage) in enumerate(progs):
        rs = gravid_rings if (gravid_rings and stage >= 2.0) else rings
        if stage_rings:
            rs = stage_rings(stage)
        for u in rs:
            if width_profile:
                wf = width_profile(stage, u)
            else:
                wf = front_narrow + (1.0 - front_narrow) * nh.smoothstep(0.0, 0.85, u)
            if round_end and i == len(progs) - 1 and u > 0.5:
                wf *= 1.0 - 0.15 * (u - 0.5) / 0.5
            ww = w * wf
            th = max(ww * thickness, min_thickness)
            stations.append((s0 + u * l, ww, th,
                             lambda v, t, i=i, u=u, p=(l, w, stage): paint(i, p, u, v, t)))
        s0 += l
    if round_end:
        l, w, stage = progs[-1]
        for u, f in ((0.985, 0.72), (1.0, 0.38)):
            ww = w * f
            stations.append((s0 - l + u * l, ww, max(ww * thickness * 0.8, min_thickness * 0.7),
                             lambda v, t, i=len(progs) - 1, u=u, p=progs[-1]: paint(i, p, u, v, t)))

    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}
    loops = []
    prev_side = None
    for s, w, th, cfn in stations:
        p, t = path.at(s)
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 0.2 and prev_side is not None:
            side = prev_side - t * prev_side.dot(t)
        side.normalize()
        prev_side = side
        up = side.cross(t).normalized()
        if bank:
            a = bank * math.sin(s * 2.3) * nh.smoothstep(neck_len, neck_len * 3, s)
            side, up = side * math.cos(a) + up * math.sin(a), up * math.cos(a) - side * math.sin(a)
        ring = []
        for x, z in sec:
            v = bm.verts.new(p + side * (x * w * 0.5) + up * (z * th * 0.5))
            vcol[v] = cfn(x, 1 if z > 0.05 else (-1 if z < -0.05 else 0))
            ring.append(v)
        loops.append(ring)
    n = len(sec)
    for a, b in zip(loops, loops[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)
    return bm


def taenia_paint(seed=0.0, cream=CREAM, gravid=GRAVID, uterus=UTERUS):
    """Default proglottid colours: the groove at each front edge shaded, immature ones pale
    ivory, mature ones cream, gravid ones warmer. With a midline vertex in the section
    (sides=8) and a middle ring (gravid_rings), the egg-filled uterus also shows darker
    down the midline with its side branches either side."""
    def paint(i, prog, u, v, top):
        l, w, stage = prog
        if stage < 1.0:
            c = nh.lerp(IVORY, cream, stage)
        else:
            c = nh.lerp(cream, gravid, min(1.0, stage - 1.0))
        if stage > 1.6 and top != 0:
            k = min(1.0, (stage - 1.6) / 0.4)
            mid = math.exp(-(v / 0.25) ** 2)                      # median stem
            branch = math.exp(-((abs(v) - 0.5) / 0.3) ** 2) * math.sin(math.pi * u) ** 2
            c = nh.lerp(c, uterus, k * min(1.0, 0.75 * mid + 0.55 * branch))
        if u < 0.02:
            c = tuple(x * GROOVE_SHADE for x in c)
        jitter = 1.0 + 0.035 * noise.noise(Vector((i * 0.37, seed, u)))
        return tuple(min(1.0, x * jitter) for x in c)
    return paint


# ---------------------------------------------------------------- scolex

def frame(pos, axis):
    """Matrix mapping local coordinates (local Y = axis forward, local Z = 'up') to world."""
    a = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    side = a.cross(ref).normalized()
    up = side.cross(a).normalized()
    m = Matrix((
        (side.x, a.x, up.x, pos.x),
        (side.y, a.y, up.y, pos.y),
        (side.z, a.z, up.z, pos.z),
        (0, 0, 0, 1),
    ))
    return m


def sucker(center, outward, radius):
    """A cup-shaped sucker: a raised muscular rim with a dark hollow in the middle."""
    parts = []
    o = outward.normalized()
    ref = Vector((0, 0, 1)) if abs(o.z) < 0.9 else Vector((1, 0, 0))
    a = o.cross(ref).normalized()
    b = o.cross(a)
    rim = [center + (a * math.cos(k / 10 * math.tau) + b * math.sin(k / 10 * math.tau)) * radius * 0.78
           for k in range(11)]
    parts.append((nh.tube(rim, [radius * 0.26] * 11, sides=6, cap_start=False, cap_end=False), SUCKER))
    m = Matrix((
        (a.x, b.x, o.x, 0), (a.y, b.y, o.y, 0), (a.z, b.z, o.z, 0), (0, 0, 0, 1)))
    cup = nh.ellipsoid(radii=(radius * 0.7, radius * 0.7, radius * 0.22), subdivisions=1, rotation=m)
    nh.transform(cup, Matrix.Translation(center - o * radius * 0.05))
    parts.append((cup, SUCKER_CUP))
    return parts


def scolex_taenia(pos, axis, radius, hooks=0, hook_size=1.0, color=CREAM, rostellum_color=SUCKER):
    """Knob-like scolex with four suckers; hooks > 0 adds a rostellum crowned with two rings
    of `hooks` hooks each (large ones alternating with small ones)."""
    M = frame(pos, axis)
    R = radius
    parts = []

    def squarish(n):
        # a slightly four-cornered knob (Taenia scoleces are quadrate seen end-on)
        return 1.0 + 0.08 * math.cos(4 * math.atan2(n.z, n.x) - math.pi) * (1 - abs(n.y))
    head = nh.ellipsoid(radii=(R, R * 0.95, R), subdivisions=2, deform=squarish)
    parts.append((head, color))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        out = Vector((math.cos(a), 0.25, math.sin(a))).normalized()
        for bm, c in sucker(out * R * 0.9, out, R * 0.42):
            parts.append((bm, c))
    if hooks:
        ry = R * 0.86
        parts.append((nh.ellipsoid((0, ry, 0), (R * 0.36, R * 0.3, R * 0.36), subdivisions=2), rostellum_color))
        for ring, (rad, size, y) in enumerate(((R * 0.36, 0.30, ry + R * 0.02), (R * 0.27, 0.22, ry + R * 0.16))):
            for k in range(hooks):
                a = (k + 0.5 * ring) / hooks * math.tau
                out = Vector((math.cos(a), 0, math.sin(a)))
                base = Vector((0, y, 0)) + out * rad
                L = R * size * hook_size
                pts = [base, base + out * L * 0.55 + Vector((0, L * 0.35, 0)),
                       base + out * L * 1.0 + Vector((0, L * 0.05, 0))]
                parts.append((nh.tube(pts, [L * 0.16, L * 0.1, 0.0], sides=3), HOOK))
    else:
        # unarmed: a shallow apical dimple instead of a rostellum
        parts.append((nh.ellipsoid((0, R * 0.9, 0), (R * 0.25, R * 0.1, R * 0.25), subdivisions=1),
                      nh.lerp(color, SUCKER_CUP, 0.35)))
    out = []
    for bm, c in parts:
        nh.transform(bm, M)
        out.append((bm, c))
    return out


def scolex_bothria(pos, axis, radius, length=2.6, color=CREAM, groove=(0.45, 0.34, 0.22)):
    """Elongate, spoon-shaped scolex flattened top to bottom, with a deep slit-like bothrium
    (sucking groove) running along its upper and its lower face."""
    M = frame(pos, axis)
    R = radius
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=16, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        x, y, z = n.x, n.z, n.y          # poles on the long (local Y) axis
        # widest in front of the middle, tapering back into the neck
        taper = 1.0 - 0.35 * nh.smoothstep(0.0, -1.0, y)
        gx = math.exp(-(x / 0.32) ** 2) * (1.0 - nh.smoothstep(0.7, 0.95, abs(y)))
        zz = z * (1.0 - 0.75 * gx)       # the grooves bite deep into both faces
        v.co = Vector((x * R * taper, y * R * length * 0.5, zz * R * 0.62 * taper))
    nh.transform(bm, Matrix.Translation(Vector((0, R * length * 0.32, 0))))

    Mi = M.inverted()

    def col(co, n):
        co = Mi @ co
        x = co.x / R
        y = (co.y - R * length * 0.32) / (R * length * 0.5)
        g = math.exp(-(x / 0.2) ** 2) * (1.0 - nh.smoothstep(0.65, 0.9, abs(y)))
        return nh.lerp(color, groove, g)
    nh.transform(bm, M)
    return [(bm, col)]


def center_object(obj):
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
