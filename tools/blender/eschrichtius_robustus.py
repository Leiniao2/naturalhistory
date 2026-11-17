"""
Procedural grey whale (Eschrichtius robustus) for the map (Swim style).

A long, fairly slender baleen whale with a narrow, gently arched head that is
short compared with a right whale's and triangular seen from above, a slightly
arched mouth line, two short throat grooves on each side under the chin and a
V-shaped double blowhole. There is no dorsal fin: a low hump two-thirds of the
way back is followed by a row of small "knuckles" running down the ridge of the
tail stock. Short, paddle-shaped, pointed flippers and broad flukes with
pointed tips, a convex S-curved trailing edge and a deep median notch.

The body, hump, knuckles, flippers and flukes are lofted sections, ridge bumps
and fin slabs fused into one seamless surface (nh_model.MeshBuilder.fuse),
given raised barnacle clusters, throat-groove creases and a mouth-line groove,
then repainted analytically: mottled slate grey heavily dappled with pale
blotches, ring-shaped barnacle scars and cream barnacle clusters with orange
whale lice, densest on the head, around the blowhole and along the back.
Crisp eyes and the blowhole slits are added on top.

Usage:
  blender --background --python tools/blender/eschrichtius_robustus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GreyWhale.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import delphinus_delphis as dd  # noqa: E402  (PCHIP interpolation, loft, fin slab, curve helpers)

VOXEL = 0.0165
MAX_TRIS = None   # an even voxel grid keeps the small scars and barnacles readable

SLATE = (0.44, 0.46, 0.48)        # mottled slate grey
SLATE_DARK = (0.30, 0.32, 0.35)
SLATE_PALE = (0.64, 0.66, 0.67)   # pale dappling
SCAR = (0.86, 0.87, 0.86)         # white barnacle / lice scars
BARNACLE = (0.82, 0.78, 0.66)     # cream barnacle clusters
LICE = (0.80, 0.52, 0.30)         # orange whale lice (cyamids) around the barnacles
GROOVE = (0.17, 0.18, 0.21)
MOUTH = (0.12, 0.12, 0.14)
EYE = (0.03, 0.03, 0.035)
BLOW = (0.06, 0.06, 0.07)

Y_TIP, Y_PED = -1.0, 0.80     # snout tip, end of the tail stock
Y_CORNER = -0.70              # mouth corner (eye just above and behind)
Y_HUMP = 0.20
KNUCKLES = 9                  # row of knuckles from behind the hump to the flukes


# ---------------------------------------------------------------- body profile

HALF_W = [(-1.0, 0.018), (-0.975, 0.045), (-0.92, 0.068), (-0.84, 0.094), (-0.74, 0.120),
          (-0.64, 0.145), (-0.50, 0.166), (-0.30, 0.178), (-0.08, 0.175), (0.12, 0.156),
          (0.32, 0.118), (0.50, 0.072), (0.64, 0.040), (0.74, 0.028), (0.80, 0.026)]
HALF_H_TOP = [(-1.0, 0.012), (-0.975, 0.030), (-0.92, 0.048), (-0.84, 0.068), (-0.74, 0.090),
              (-0.66, 0.112), (-0.54, 0.142), (-0.34, 0.165), (-0.10, 0.170), (0.12, 0.162),
              (0.32, 0.142), (0.50, 0.112), (0.64, 0.082), (0.74, 0.058), (0.80, 0.038)]
HALF_H_BOT = [(-1.0, 0.014), (-0.975, 0.036), (-0.92, 0.062), (-0.84, 0.090), (-0.74, 0.116),
              (-0.62, 0.145), (-0.45, 0.170), (-0.22, 0.180), (0.02, 0.172), (0.20, 0.150),
              (0.38, 0.115), (0.54, 0.082), (0.66, 0.058), (0.74, 0.042), (0.80, 0.032)]
CENTER_Z = [(-1.0, -0.035), (-0.86, -0.025), (-0.62, -0.005), (-0.3, 0.0), (0.5, 0.0), (0.8, 0.008)]


def w(y): return dd._interp(HALF_W, y)
def ht(y): return dd._interp(HALF_H_TOP, y)
def hb(y): return dd._interp(HALF_H_BOT, y)
def zc(y): return dd._interp(CENTER_Z, y)


def knuckle_ys():
    y0, y1 = Y_HUMP + 0.13, 0.71
    return [y0 + (y1 - y0) * i / (KNUCKLES - 1) for i in range(KNUCKLES)]


def ridge(y):
    """Extra height on the dorsal midline: the low hump and the ridge along the tail stock."""
    r = 0.050 * math.exp(-((y - Y_HUMP) / 0.075) ** 2)
    r += 0.012 * nh.smoothstep(Y_HUMP, Y_HUMP + 0.15, y) * (1.0 - nh.smoothstep(0.70, 0.80, y))
    return r


def keel(y):
    """Low ventral keel along the underside of the tail stock."""
    return 0.012 * nh.smoothstep(0.38, 0.55, y) * (1.0 - nh.smoothstep(0.70, 0.80, y))


def section(y, a, n=2.2):
    """Superellipse cross-section point at angle a (0 = +x, pi/2 = up), with a sharp
    dorsal ridge (hump, tail-stock ridge) and a ventral keel on the narrowing tail stock."""
    c, s = math.cos(a), math.sin(a)
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    z = zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)
    if s > 0:
        z += ridge(y) * s ** 8
    else:
        z -= keel(y) * (-s) ** 8
    return Vector((x, y, z))


# ---------------------------------------------------------------- fins

def knuckles():
    """The row of knuckles on the dorsal ridge: small bumps, shrinking toward the flukes."""
    out = []
    for i, ky in enumerate(knuckle_ys()):
        k = 1.0 - 0.45 * i / (KNUCKLES - 1)
        top = zc(ky) + ht(ky) + ridge(ky)
        out.append(nh.ellipsoid((0.0, ky, top - 0.002), (0.019 * k, 0.021 * k, 0.027 * k), subdivisions=2))
    return out


def flukes():
    """Broad flukes: pointed tips, convex S-curved trailing edge, deep median notch."""
    half = [(0.0, 0.74), (0.05, 0.775)] + dd.curve((0.05, 0.775), (0.27, 0.93), -0.12, 9) \
        + dd.curve((0.27, 0.93), (0.13, 0.975), 0.10, 6) + dd.curve((0.13, 0.975), (0.025, 0.925), -0.10, 5) \
        + [(0.025, 0.925), (0.0, 0.905)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    th = [0.06 - 0.032 * min(1.0, abs(x) / 0.27) for x, _y in pts]
    return dd.fin_slab(pts, th, lambda u, v: (Vector((u, v, zc(Y_PED))), Vector((0.0, 0.0, 1.0))))


def flipper(sign):
    """Short, paddle-shaped, pointed flipper set low on the flank behind the head."""
    droop, sweep = math.radians(34), 0.75
    def frame(u, v):
        x = sign * (w(u) * 0.80 + v * math.cos(droop))
        z = zc(u) - hb(u) * 0.50 - v * math.sin(droop)
        return Vector((x, u + v * sweep, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    a, b = (-0.60, 0.0), (-0.49, 0.0)
    tip = (-0.565, 0.24)
    pts = [a] + dd.curve(a, tip, 0.16, 8) + dd.curve(tip, b, 0.20, 8) + [b]
    th = [0.055 - 0.03 * min(1.0, v / 0.24) for _u, v in pts]
    return dd.fin_slab(pts, th, frame)


# ---------------------------------------------------------------- surface pattern

def rel_z(p):
    """-1 (belly) .. 1 (back) across the flank at the point's y."""
    y = max(min(p.y, Y_PED), Y_TIP)
    d = p.z - zc(y)
    return d / max(ht(y) if d >= 0 else hb(y), 1e-3)


def outside(p):
    """How far a point sits outside the body envelope (0 on the body), to find the fins."""
    y = max(min(p.y, Y_PED), Y_TIP)
    hz = ht(y) if p.z >= zc(y) else hb(y)
    r = math.sqrt((p.x / max(w(y), 1e-3)) ** 2 + ((p.z - zc(y)) / max(hz, 1e-3)) ** 2)
    return max(0.0, r - 1.0) * min(w(y), hz)


def mouth_z(y):
    """Slightly arched mouth line from the snout tip back to the corner."""
    t = max(0.0, min(1.0, (y - Y_TIP) / (Y_CORNER - Y_TIP)))
    return zc(y) - hb(y) * 0.05 + 0.020 * math.sin(t * math.pi) - 0.012 * t


def mouth_amount(p):
    y = p.y
    if not Y_TIP < y < Y_CORNER + 0.01:
        return 0.0
    d = abs(p.z - mouth_z(y))
    fade = 1.0 - nh.smoothstep(Y_CORNER - 0.01, Y_CORNER + 0.01, y)
    return (1.0 - nh.smoothstep(0.003, 0.008, d)) * fade


GROOVES = [(-0.042, -0.86, -0.74), (-0.088, -0.84, -0.735), (0.042, -0.86, -0.74), (0.088, -0.84, -0.735)]


def groove_amount(p):
    """Two short throat grooves on each side of the chin."""
    if p.z > zc(p.y) - hb(p.y) * 0.55:
        return 0.0
    best = 0.0
    for gx, y0, y1 in GROOVES:
        if not y0 < p.y < y1:
            continue
        ends = nh.smoothstep(y0, y0 + 0.02, p.y) * (1.0 - nh.smoothstep(y1 - 0.02, y1, p.y))
        cx = gx * (0.85 + 0.15 * (p.y - y0) / (y1 - y0))
        best = max(best, (1.0 - nh.smoothstep(0.003, 0.009, abs(p.x - cx))) * ends)
    return best


def _cells(p, freq, seed):
    """Distance (in cell units) to the nearest Voronoi feature, plus a per-cell random value."""
    q = p * freq + Vector(seed)
    d, pts = noise.voronoi(q)
    rnd = noise.noise(pts[0] * 3.7 + Vector((1.3, 2.9, 0.4))) * 0.5 + 0.5
    return d[0], rnd


def barnacle_density(p):
    """Where barnacle clusters are thickest: top and sides of the head, around the blowhole,
    the hump and the back, scattered elsewhere (the belly stays fairly clean)."""
    y, r = p.y, rel_z(p)
    head = 1.0 - nh.smoothstep(-0.60, -0.48, y)
    back = nh.smoothstep(-0.1, 0.4, r) * (1.0 - nh.smoothstep(0.55, 0.72, y))
    hump = math.exp(-((y - Y_HUMP) / 0.15) ** 2) * nh.smoothstep(0.0, 0.5, r)
    blob = noise.noise(p * 3.0 + Vector((5.0, 1.0, 3.0))) * 0.5 + 0.5
    d = 0.08 + 0.75 * head * nh.smoothstep(-0.6, 0.2, r) + 0.45 * back + 0.35 * hump
    return min(1.0, d * (0.45 + 0.9 * blob))


def barnacle_amount(p):
    """0..1 inside a barnacle cluster: irregular crusty blobs (fractal noise) plus a few
    small isolated barnacles (Voronoi cells), thresholded by barnacle_density()."""
    if outside(p) > 0.02:   # flipper leading edges carry a few, flukes hardly any
        dens = 0.3 if p.y < 0.0 else 0.0
    else:
        dens = barnacle_density(p)
    if dens <= 0.0:
        return 0.0
    m = noise.fractal(p * 8.0 + Vector((2.0, 5.0, 9.0)), 0.6, 2.2, 3)
    thr = 0.80 - 0.80 * dens
    blob = nh.smoothstep(thr - 0.06, thr + 0.06, m)
    dist, rnd = _cells(p, 18.0, (0.0, 0.0, 0.0))
    single = 0.0
    if rnd < dens * 0.5:
        single = 1.0 - nh.smoothstep(0.17, 0.25, dist + noise.noise(p * 70.0) * 0.06)
    return max(blob, single)


def body_color(p, n):
    y = p.y
    fin = outside(p) > 0.012 or y > Y_PED + 0.02
    r = rel_z(p)

    # mottled slate: darker on the back, a little paler below, large soft blotches
    col = nh.lerp(SLATE, SLATE_DARK, nh.smoothstep(0.1, 0.9, r) * 0.6)
    col = nh.lerp(col, (0.38, 0.40, 0.42), nh.smoothstep(-0.3, -0.9, r) * 0.6)
    big = noise.noise(p * 5.0 + Vector((2.0, 7.0, 1.0)))
    col = nh.lerp(col, SLATE_DARK, nh.smoothstep(0.1, 0.5, big) * 0.5)
    # dense pale dappling (old healed scars), all over the body
    mid = noise.noise(p * 16.0 + Vector((9.0, 3.0, 4.0)))
    col = nh.lerp(col, SLATE_PALE, nh.smoothstep(0.25, 0.45, mid) * 0.75)
    d, rnd = _cells(p, 15.0, (11.0, 4.0, 8.0))
    if rnd > 0.40:
        sz = 0.16 + 0.22 * (rnd - 0.40) / 0.60
        d += noise.noise(p * 45.0) * 0.08
        col = nh.lerp(col, nh.lerp(SLATE_PALE, SCAR, (rnd - 0.40) / 0.60), (1.0 - nh.smoothstep(sz - 0.10, sz + 0.02, d)) * 0.95)
    # ring-shaped scars where barnacles fell off (pale ring, grey centre)
    d, rnd = _cells(p, 11.0, (3.0, 13.0, 6.0))
    if rnd > 0.72:
        ring = 1.0 - nh.smoothstep(0.03, 0.10, abs(d + noise.noise(p * 40.0) * 0.05 - 0.22))
        col = nh.lerp(col, SCAR, ring * 0.7)
    if fin:
        col = nh.lerp(col, SLATE_DARK, 0.3)

    # barnacle clusters: cream crust with orange whale lice in and around it
    b = barnacle_amount(p)
    if b > 0.0:
        lice = noise.noise(p * 95.0 + Vector((4.0, 4.0, 4.0)))
        crust = nh.lerp(BARNACLE, LICE, nh.smoothstep(0.30, 0.50, lice) * 0.85)
        grain = noise.noise(p * 160.0) * 0.08
        crust = tuple(max(0.0, c - grain) for c in crust)
        col = nh.lerp(col, crust, b)

    # mouth line, throat grooves
    col = nh.lerp(col, MOUTH, mouth_amount(p) * 0.9)
    col = nh.lerp(col, GROOVE, groove_amount(p) * 0.8)
    return col


def skin_detail(bm):
    """Raised barnacle clusters, throat-groove creases, the mouth-line groove and a faint ripple."""
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 30.0) * 0.0008
        d += barnacle_amount(p) * (0.006 + noise.noise(p * 120.0) * 0.002)
        d -= groove_amount(p) * 0.006
        d -= mouth_amount(p) * 0.005
        v.co = p + v.normal * d


# ---------------------------------------------------------------- build

def blowhole(sign):
    """One of the paired blowhole slits; together they form a V on top of the head."""
    y = -0.645
    bm = nh.ellipsoid((0, 0, 0), (0.0045, 0.022, 0.005), subdivisions=2)
    nh.transform(bm, Matrix.Rotation(sign * math.radians(-18), 4, "Z"))
    nh.transform(bm, Matrix.Translation(Vector((sign * 0.012, y, zc(y) + ht(y) - 0.001))))
    return bm


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)   # repainted after fusing
    parts.add(dd.loft(Y_TIP, Y_PED + 0.02, 150, 44, section), grey)
    parts.add(flukes(), grey)
    for kn in knuckles():
        parts.add(kn, grey)
    for sg in (-1, 1):
        parts.add(flipper(sg), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5, max_tris=MAX_TRIS)
    skin_detail(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, body_color)
    for sg in (-1, 1):
        y = Y_CORNER + 0.012
        z = mouth_z(Y_CORNER) + 0.022
        mb.add(nh.ellipsoid((sg * w(y) * 0.95, y, z), (0.008, 0.011, 0.008), subdivisions=2), EYE)
        mb.add(blowhole(sg), BLOW)

    return mb.to_object("GreyWhale", roughness=0.55)


def closeup(path, cam_loc, target, lens=55):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "GreyWhale")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, background=(0.05, 0.18, 0.24),
                          views=((35, 25), (-90, 4), (90, 4), (30, 62), (180, -40)))
        closeup(out.with_name(f"{out.stem}_head.png"), (0.75, -1.75, 0.25), (0.0, -0.78, -0.02), lens=50)
        closeup(out.with_name(f"{out.stem}_throat.png"), (0.55, -1.55, -0.75), (0.0, -0.80, -0.10), lens=50)
        closeup(out.with_name(f"{out.stem}_back.png"), (1.3, 0.35, 0.45), (0.0, 0.42, 0.10), lens=50)


if __name__ == "__main__":
    main()
