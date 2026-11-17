"""
Procedural Leedsichthys problematicus (Middle-Late Jurassic pachycormid) for the map (Swim style).

The largest known bony fish: a giant, slow suspension feeder of Callovian-Oxfordian seas
(Oxford Clay of England and equivalents in France, Germany and Chile), with growth series
suggesting adults of roughly 8-16.5 m. The skeleton was mostly cartilage, so the fossils are
scrappy (gill rakers, fin rays, parts of the skull and tail); the body follows the usual
pachycormid plan and published reconstructions: a long, fusiform bony-fish body; a big,
blunt head with the lower jaw dropped in a wide gape that shows the sieve of gill rakers
across the back of the throat; long, narrow, scythe-shaped pectoral fins; a single falcate
dorsal fin near mid-body; a small anal fin; and a tall, deeply forked tail with narrow lobes.
Pelvic fins are small or absent in pachycormids and are left out. Dark blue-grey above,
pale below, with faint mottling and fine scale grain.

The body, upper head and median fins are lofted / slabbed (helpers from otodus_megalodon.py),
fused into one seamless surface (nh_model.MeshBuilder.fuse), given an opercular groove, a
lateral line and scale grain, then repainted procedurally. The dropped lower jaw is fused
separately and hinged open. Eyes, the pectoral fins and the gill rakers (placed on the throat
wall by ray casts through the open mouth) are crisp shells.

rhinconichthys_taylori.py reuses this file with its own proportions (module-level P).

Usage:
  blender --background --python tools/blender/leedsichthys_problematicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Leedsichthys.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import otodus_megalodon as om  # noqa: E402  (loft / fin-slab / interpolation helpers)
import nh_fish as fish  # noqa: E402  (crisp gridded fins)

# Everything species-specific lives in P so other pachycormids can swap it out.
P = dict(
    name="Leedsichthys",
    voxel=0.019, jaw_voxel=0.016,
    y_tip=-1.00, y_ped=0.64, y_hinge=-0.64,
    gape=math.radians(30),      # lower jaw dropped
    snout_up=math.radians(0),   # upper head tilted up about the hinge
    palate=0.30,                # fraction of the belly depth left under the upper head
    jaw_w=0.95,
    half_w=[(-1.00, 0.03), (-0.96, 0.10), (-0.88, 0.155), (-0.74, 0.19), (-0.50, 0.205), (-0.20, 0.19),
            (0.10, 0.15), (0.36, 0.095), (0.56, 0.05), (0.64, 0.04)],
    half_top=[(-1.00, 0.03), (-0.96, 0.085), (-0.88, 0.135), (-0.74, 0.175), (-0.50, 0.21),
              (-0.20, 0.205), (0.10, 0.16), (0.36, 0.10), (0.56, 0.055), (0.64, 0.045)],
    half_bot=[(-1.00, 0.03), (-0.96, 0.08), (-0.88, 0.13), (-0.74, 0.17), (-0.50, 0.20),
              (-0.20, 0.19), (0.10, 0.145), (0.36, 0.09), (0.56, 0.05), (0.64, 0.04)],
    center_z=[(-1.00, 0.0), (-0.6, 0.0), (0.0, 0.0), (0.64, 0.01)],
    pect=dict(y_front=-0.50, chord=0.14, sweep=0.48, span=0.76, droop=14, lead=0.08, trail=0.50, th=0.030),
    dorsal=dict(y0=-0.10, y1=0.14, height=0.24, rake=0.16),
    anal=dict(y0=0.30, y1=0.40, height=0.10, rake=0.06),
    caudal=dict(y_root=0.55, up=(1.02, 0.60), lo=(1.00, -0.56), fork=(0.79, 0.01), th=0.07),
    eye=dict(y=-0.86, up=0.28, r=0.022),
    opercle=0.08,               # opercular groove this far behind the hinge
    rakers=dict(cols=24, rows=12, r=0.0025),
    colors=dict(back=(0.17, 0.21, 0.25), flank=(0.42, 0.47, 0.50), belly=(0.83, 0.83, 0.80),
                fin_edge=(0.12, 0.14, 0.17), mouth=(0.24, 0.12, 0.12), throat=(0.10, 0.06, 0.06),
                lip=(0.55, 0.47, 0.44), raker=(0.66, 0.60, 0.50), eye=(0.04, 0.04, 0.05),
                eye_ring=(0.55, 0.55, 0.50), groove=(0.12, 0.13, 0.15), line=(0.55, 0.58, 0.60)),
    preview=dict(background=(0.05, 0.16, 0.20), views=((35, 25), (90, 4), (30, 62), (-15, 8))),
)


# ---------------------------------------------------------------- profile

def w(y): return om._interp(P["half_w"], y)
def ht(y): return om._interp(P["half_top"], y)
def hb(y): return om._interp(P["half_bot"], y)
def zc(y): return om._interp(P["center_z"], y)
def top_z(y): return zc(y) + ht(y)
def bot_z(y): return zc(y) - hb(y)
def palate_z(y): return zc(y) - hb(y) * P["palate"]


def hinge():
    y = P["y_hinge"]
    return Vector((0.0, y, palate_z(y) - 0.01))


def about_hinge(angle):
    h = hinge()
    return Matrix.Translation(h) @ Matrix.Rotation(angle, 4, "X") @ Matrix.Translation(-h)


def jaw_matrix(): return about_hinge(P["gape"])
def snout_matrix(): return about_hinge(-P["snout_up"])


def superellipse(y, a, half_w, z_top, z_bot, n):
    c, s = math.cos(a), math.sin(a)
    x = half_w * math.copysign(abs(c) ** (2.0 / n), c)
    mid, half = (z_top + z_bot) * 0.5, (z_top - z_bot) * 0.5
    if s >= 0:
        z = mid + half * abs(s) ** (2.0 / n)
    else:
        z = mid - half * abs(s) ** (2.0 / n)
    return Vector((x, y, z))


def body_point(y, a):
    """Full body section: rounded back, slightly fuller belly."""
    c, s = math.cos(a), math.sin(a)
    n = 2.2
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    return Vector((x, y, zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)))


def upper_head_point(y, a):
    """Upper head over the mouth: full skull above, a flat palate underneath."""
    c, s = math.cos(a), math.sin(a)
    n = 2.2
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    if s >= 0:
        z = zc(y) + ht(y) * abs(s) ** (2.0 / n)
    else:
        depth = zc(y) - palate_z(y)
        z = zc(y) - depth * abs(s) ** (2.0 / 3.5)
    return Vector((x, y, z))


def lower_jaw_point(y, a):
    """Lower jaw in its closed pose: from just under the palate to the belly line, a little
    narrower than the head, with a sunken floor (the mouth) between the rami."""
    hw = w(y) * P["jaw_w"]
    zt, zb = palate_z(y) - 0.004, bot_z(y)
    p = superellipse(y, a, hw, zt, zb, 2.4)
    if math.sin(a) > 0:
        back = nh.smoothstep(P["y_hinge"] - 0.12, P["y_hinge"] + 0.05, y)
        sink = max(0.0, 1.0 - (abs(p.x) / max(hw * 0.80, 1e-4)) ** 2) * (1.0 - back)
        p.z -= (zt - zb) * 0.55 * sink
    return p


# ---------------------------------------------------------------- fins

def dorsal():
    d = P["dorsal"]
    y0, y1 = d["y0"], d["y1"]
    base = lambda y: top_z(y) - 0.04  # noqa: E731
    a, b = (y0, base(y0)), (y1, base(y1))
    apex = (y0 + (y1 - y0) * 0.55 + d["rake"], top_z((y0 + y1) / 2) + d["height"])
    notch = (y1 + 0.03, base(y1) + 0.05)
    pts = [a] + om.curve(a, apex, -0.07, 8) + om.curve(apex, notch, 0.14, 7) + [notch, b]
    th = om.taper(pts, base(y0) + 0.03, apex[1], 0.065, 0.046)
    return om.fin_slab(pts, th, om.midline_frame)


def anal():
    d = P["anal"]
    y0, y1 = d["y0"], d["y1"]
    base = lambda y: bot_z(y) + 0.03  # noqa: E731
    a, b = (y0, base(y0)), (y1, base(y1))
    apex = (y0 + (y1 - y0) * 0.5 + d["rake"], bot_z((y0 + y1) / 2) - d["height"])
    trail = (y1 + d["rake"] * 0.6, base(y1) - d["height"] * 0.25)
    pts = [a] + om.curve(a, apex, 0.10, 5) + om.curve(apex, trail, -0.12, 4) + [trail, b]
    th = om.taper(pts, -base(y0), -apex[1], 0.06, 0.046)
    return om.fin_slab(pts, th, om.midline_frame)


def caudal():
    """Tall, deeply forked tail with narrow, pointed lobes (homocercal, near-symmetric)."""
    d = P["caudal"]
    yr = d["y_root"]
    top_root, bot_root = (yr, top_z(yr) - 0.01), (yr + 0.01, bot_z(yr) + 0.01)
    up, lo, fork = d["up"], d["lo"], d["fork"]
    pts = ([top_root] + om.curve(top_root, up, -0.10, 10) + om.curve(up, fork, 0.10, 9)
           + om.curve(fork, lo, 0.10, 9) + om.curve(lo, bot_root, -0.10, 10))
    th = []
    for (u, v) in pts:
        k = (Vector((u, v)) - Vector((yr, zc(yr)))).length / 0.6
        th.append(d["th"] + (0.046 - d["th"]) * min(1.0, k))
    return om.fin_slab(pts, th, om.midline_frame)


def pectoral(mb, sign):
    """Long, narrow, scythe-shaped pectoral (convex leading edge, concave trailing edge), built
    as a crisp gridded fin (nh_fish.fin) rooted inside the flank: a thin fin lying oblique to
    the voxel grid would come out ragged if fused."""
    d = P["pect"]
    droop = math.radians(d["droop"])
    yf = d["y_front"]
    x0 = w(yf) * 0.72
    z0 = zc(yf) - hb(yf) * 0.55

    def at(u, v):
        return (sign * (x0 + v * math.cos(droop)), u, z0 - v * math.sin(droop))

    ra, rb = (yf, 0.0, 0.0), (yf + d["chord"], 0.0, 0.0)
    tip = (yf + d["sweep"], d["span"], 0.0)
    lc = (yf + d["sweep"] * d["lead"], d["span"] * 0.6, 0.0)
    tc = (yf + d["sweep"] * d["trail"], d["span"] * 0.55, 0.0)
    n = 16
    lead = [at(*fish.bezier(ra, lc, tip, i / (n - 1))[:2]) for i in range(n)]
    trail = [at(*fish.bezier(rb, tc, tip, i / (n - 1))[:2]) for i in range(n)]
    C = P["colors"]
    flank = nh.lerp(C["flank"], C["back"], 0.4)

    def color(u, v, co):
        return nh.lerp(nh.lerp(flank, C["belly"], 0.25 * (1 - u)), C["fin_edge"], nh.smoothstep(0.45, 1.0, u) * 0.8)

    fish.fin(mb, lead, trail, color, rows=3, th0=d["th"], th1=d["th"] * 0.35)


# ---------------------------------------------------------------- surface detail

def opercle_amount(p):
    """Groove along the back edge of the gill cover, curving forward at the bottom."""
    y = P["y_hinge"] + P["opercle"]
    if abs(p.x) < w(y) * 0.5:
        return 0.0
    rel = (p.z - zc(y)) / max(ht(y), 1e-3)
    if not -0.9 < rel < 0.75:
        return 0.0
    cy = y + 0.05 * (1.0 - rel * rel) - 0.03 * max(0.0, -rel)
    ends = nh.smoothstep(-0.9, -0.7, rel) * (1.0 - nh.smoothstep(0.55, 0.75, rel))
    return (1.0 - nh.smoothstep(0.004, 0.013, abs(p.y - cy))) * ends


def in_mouth(p):
    """1 inside the open mouth (under the palate, in front of the hinge, between the jaws)."""
    q = snout_matrix().inverted() @ p
    y = q.y
    if y > P["y_hinge"] + 0.04 or y < P["y_tip"] + 0.01:
        return 0.0
    inside = 1.0 - nh.smoothstep(0.80, 0.95, abs(q.x) / max(w(y), 1e-3))
    below = nh.smoothstep(palate_z(y) + 0.01, palate_z(y) - 0.005, q.z)
    return inside * below


def body_color(p, n):
    C = P["colors"]
    y = max(min(p.y, P["y_ped"]), P["y_tip"])
    belly = nh.smoothstep(-0.1, -0.6, n.z) * (1.0 - nh.smoothstep(0.45, 0.62, p.y))
    wav = noise.noise(Vector((p.y * 4.0, 0.0, 2.1))) * 0.03
    belly = max(belly, 1.0 - nh.smoothstep(zc(y) - hb(y) * 0.35 + wav - 0.02, zc(y) - hb(y) * 0.35 + wav + 0.02, p.z))
    belly *= 1.0 - nh.smoothstep(0.50, 0.62, p.y)
    up = nh.smoothstep(zc(y) - 0.05, top_z(y) + 0.05, p.z)
    c = nh.lerp(C["flank"], C["back"], up)
    mott = noise.noise(p * 6.0) * 0.5 + 0.5
    c = nh.lerp(c, tuple(v * 0.82 for v in c), mott * 0.45)
    # pectorals: dark above, paler below
    out_x = abs(p.x) - w(y) * 1.05
    if out_x > 0.02 and p.y < 0.2:
        belly = nh.smoothstep(0.1, -0.3, n.z) * 0.7
    c = nh.lerp(c, C["belly"], belly)
    # dark fin margins (beyond the body outline)
    out = max(0.0, out_x) + max(0.0, p.z - top_z(y) - 0.03) + max(0.0, bot_z(y) - p.z - 0.03) \
        + max(0.0, p.y - P["y_ped"]) * 0.8
    c = nh.lerp(c, C["fin_edge"], nh.smoothstep(0.12, 0.40, out) * 0.75)
    # lateral line
    if P["y_hinge"] + 0.1 < p.y < P["y_ped"] and abs(p.x) > w(y) * 0.6:
        lz = zc(y) + ht(y) * 0.30 - 0.06 * (p.y + 0.3) ** 2
        c = nh.lerp(c, C["line"], (1.0 - nh.smoothstep(0.003, 0.009, abs(p.z - lz))) * 0.55)
    # gill cover a shade darker / browner than the flank, edged by the opercular groove
    if p.y < P["y_hinge"] + P["opercle"] + 0.05 and abs(p.x) > w(y) * 0.5:
        rel = (p.z - zc(y)) / max(ht(y), 1e-3)
        yo = P["y_hinge"] + P["opercle"] + 0.05 * (1.0 - rel * rel) - 0.03 * max(0.0, -rel)
        cover = (1.0 - nh.smoothstep(yo - 0.02, yo, p.y)) * nh.smoothstep(-0.9, -0.6, rel) \
            * nh.smoothstep(P["y_hinge"] - 0.08, P["y_hinge"] + 0.0, p.y)
        c = nh.lerp(c, tuple(v * 0.80 for v in c), cover * 0.6)
    # cycloid scales: faint darker rims on a staggered grid along the flank
    if P["y_hinge"] + P["opercle"] < p.y < P["y_ped"] and out < 0.01:
        cell = noise.voronoi(Vector((p.y * 38.0, p.z * 38.0, abs(p.x) * 4.0)))[0]
        rim = nh.smoothstep(0.08, 0.0, cell[1] - cell[0])
        c = nh.lerp(c, tuple(v * 0.78 for v in c), rim * 0.35)
    c = nh.lerp(c, C["groove"], opercle_amount(p) * 0.8)
    # mouth: pale lip along the edge, dark throat further in
    m = in_mouth(p)
    if m > 0:
        q = snout_matrix().inverted() @ p
        deep = nh.smoothstep(P["y_tip"] + 0.03, P["y_tip"] + 0.12, q.y)
        c = nh.lerp(c, nh.lerp(C["mouth"], C["throat"], deep), m)
    return c


def jaw_color(p, n):
    """Lower jaw, painted in its open pose: skin outside, dark mouth floor between the rami."""
    C = P["colors"]
    c = body_color(p, n)
    q = jaw_matrix().inverted() @ p
    y = q.y
    hw = max(w(y) * P["jaw_w"], 1e-3)
    if q.z > palate_z(y) - (palate_z(y) - bot_z(y)) * 0.65 and abs(q.x) < hw * 0.97:
        nn = jaw_matrix().inverted().to_3x3() @ n
        floor = nh.smoothstep(0.1, 0.5, nn.z)
        inner = 1.0 - nh.smoothstep(0.7, 0.92, abs(q.x) / hw)
        mouth = nh.lerp(C["lip"], nh.lerp(C["mouth"], C["throat"], 0.5), inner)
        c = nh.lerp(c, mouth, floor)
    return c


def skin_detail(bm, grooves=True):
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 70.0) * 0.0009 + noise.noise(p * 25.0 + Vector((2, 5, 1))) * 0.0012
        if grooves:
            d -= opercle_amount(p) * 0.010
        v.co = p + v.normal * d


# ---------------------------------------------------------------- build

def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    yh = P["y_hinge"]
    parts.add(om.loft(yh - 0.10, P["y_ped"] + 0.02, 80, 44, body_point), grey)
    head = om.loft(P["y_tip"], yh + 0.14, 44, 44, upper_head_point)
    nh.transform(head, snout_matrix())
    parts.add(head, grey)
    parts.add(dorsal(), grey)
    parts.add(anal(), grey)
    parts.add(caudal(), grey)
    fused = parts.fuse(voxel=P["voxel"], smooth=6, smooth_factor=0.5)
    skin_detail(fused)
    return fused


def build_lower_jaw():
    parts = nh.MeshBuilder()
    parts.add(om.loft(P["y_tip"] + 0.025, P["y_hinge"] + 0.08, 40, 40, lower_jaw_point), (0.5, 0.5, 0.5))
    fused = parts.fuse(voxel=P["jaw_voxel"], smooth=4, smooth_factor=0.5)
    skin_detail(fused, grooves=False)
    nh.transform(fused, jaw_matrix())
    fused.normal_update()
    return fused


def add_rakers(mb, body, jaw):
    """Gill rakers: thin pale bars on the throat wall, found by casting rays through the gape."""
    bvh_b, bvh_j = BVHTree.FromBMesh(body), BVHTree.FromBMesh(jaw)
    yh = P["y_hinge"]
    jm = jaw_matrix()
    # opening at the front: top = palate, bottom = top of the dropped jaw, at the mouth corners
    y_front = P["y_tip"] + 0.10
    z_hi = (snout_matrix() @ Vector((0, y_front, palate_z(y_front)))).z
    z_lo = (jm @ Vector((0, y_front, palate_z(y_front)))).z
    cols, rows = P["rakers"]["cols"], P["rakers"]["rows"]
    xw = w(yh - 0.05) * 0.80
    for i in range(cols):
        x = -xw + 2 * xw * (i + 0.5) / cols
        pts = []
        for k in range(rows + 1):
            z = z_lo + (z_hi - z_lo) * (0.05 + 0.9 * k / rows)
            o = Vector((x, -3.0, z))
            hb_ = bvh_b.ray_cast(o, Vector((0, 1, 0)))
            hj = bvh_j.ray_cast(o, Vector((0, 1, 0)))
            if hb_[0] is None or (hj[0] is not None and hj[3] < hb_[3]):
                continue
            if hb_[0].y < yh - 0.30:     # hit the snout / palate front, not the throat
                continue
            pts.append(hb_[0] + Vector((0, -0.006, 0)))
        if len(pts) < 3:
            continue
        mb.add(nh.tube(pts, [P["rakers"]["r"]] * len(pts), sides=4), P["colors"]["raker"], smooth=False)


def head_details(mb):
    C = P["colors"]
    e = P["eye"]
    sm = snout_matrix()
    for sx in (-1, 1):
        y = e["y"]
        z = zc(y) + ht(y) * e["up"]
        x = sx * w(y) * 0.88
        r = e["r"]
        for ctr, rad, col in (((x, y, z), (r * 0.7, r * 1.25, r * 1.15), C["eye_ring"]),
                              ((x + sx * r * 0.25, y - r * 0.1, z), (r * 0.6, r * 0.8, r * 0.75), C["eye"])):
            bm = nh.ellipsoid(ctr, rad, subdivisions=2)
            nh.transform(bm, sm)
            mb.add(bm, col)


def build():
    mb = nh.MeshBuilder()
    body = build_body()
    jaw = build_lower_jaw()
    add_rakers(mb, body, jaw)
    mb.add(body, body_color)
    mb.add(jaw, jaw_color)
    head_details(mb)
    for sg in (-1, 1):
        pectoral(mb, sg)
    return mb.to_object(P["name"], roughness=0.5)


def main():
    nh.run(build, P["name"], **P["preview"])


if __name__ == "__main__":
    main()
